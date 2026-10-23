// src/app/page.tsx

import { redirect } from "next/navigation";
import pool from "../lib/postgres";
import DashboardLayoutClient from "./DashboardLayoutClient";
import { getSsoSession } from "@/lib/sso";

/**
 * FastAPI configuration
 */
const FASTAPI_URL =
  process.env.FASTAPI_URL || "http://127.0.0.1:8000";

const AUTHENTICATION_ENDPOINT =
  `${FASTAPI_URL}/api/authentication`;


/**
 * Safely encode values used in redirect URLs.
 */
function encodeRedirectValue(value: unknown): string {
  return encodeURIComponent(
    value === undefined || value === null || value === ""
      ? "Unknown"
      : String(value)
  );
}


/**
 * Redirect to login with a diagnostic error code.
 */
function redirectToLogin(
  errorCode: string,
  userId?: unknown,
  userIc?: unknown,
  email?: unknown
): never {
  const params = new URLSearchParams();

  params.set("error", errorCode);

  if (userId !== undefined) {
    params.set("userId", encodeRedirectValue(userId));
  }

  if (userIc !== undefined) {
    params.set("userIc", encodeRedirectValue(userIc));
  }

  if (email !== undefined) {
    params.set("email", encodeRedirectValue(email));
  }

  redirect(`/login?${params.toString()}`);
}


/**
 * Main dashboard page.
 */
export default async function DashboardPage() {

  // ============================================================
  // 1. GET SSO SESSION
  // ============================================================

  let ssoSession: any;

  try {

    console.log("");
    console.log("============================================================");
    console.log("[NEXT.JS] Dashboard authentication started");
    console.log("============================================================");

    ssoSession = await getSsoSession();

    console.log("[NEXT.JS] SSO session result:", {
      success: ssoSession?.success,
      userId: ssoSession?.userId,
      userIc: ssoSession?.userIc,
      hasAuthBearer: Boolean(ssoSession?.authBearer),
      hasSmsession: Boolean(ssoSession?.smsession),
      hasSsolgenet: Boolean(ssoSession?.ssolgenet),
    });

  } catch (error) {

    console.error("");
    console.error("============================================================");
    console.error("[NEXT.JS] SSO SESSION ERROR");
    console.error("============================================================");
    console.error(error);

    redirectToLogin("session_error");
  }


  if (!ssoSession || !ssoSession.success) {

    console.error("");
    console.error("============================================================");
    console.error("[NEXT.JS] INVALID SSO SESSION");
    console.error("============================================================");
    console.error("[NEXT.JS] ssoSession:", ssoSession);

    redirectToLogin(
      "session_error",
      ssoSession?.userId,
      ssoSession?.userIc
    );
  }


  // ============================================================
  // 2. CALL FASTAPI
  // ============================================================

  let authResult: any = null;

  try {

    console.log("");
    console.log("============================================================");
    console.log("[NEXT.JS] FASTAPI AUTHENTICATION REQUEST");
    console.log("============================================================");

    const requestBody = {
      userId: ssoSession.userId,
      userIc: ssoSession.userIc,
      authBearer: ssoSession.authBearer || "",
      smsession: ssoSession.smsession || "",
      ssolgenet: ssoSession.ssolgenet || "",
    };

    const startTime = Date.now();

    let apiResponse: Response;

    try {

      apiResponse = await fetch(
        AUTHENTICATION_ENDPOINT,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
          },

          body: JSON.stringify(requestBody),

          cache: "no-store",

          signal: AbortSignal.timeout(15000),
        }
      );

    } catch (fetchError: any) {

      const duration = Date.now() - startTime;

      console.error("[NEXT.JS] FASTAPI FETCH FAILED", fetchError);

      if (
        fetchError?.name === "TimeoutError" ||
        fetchError?.name === "AbortError"
      ) {
        redirectToLogin(
          "backend_timeout",
          ssoSession.userId,
          ssoSession.userIc
        );
      }

      redirectToLogin(
        "backend_unreachable",
        ssoSession.userId,
        ssoSession.userIc
      );
    }


    const responseText = await apiResponse.text();

    if (!apiResponse.ok) {
      console.error("[NEXT.JS] FASTAPI RETURNED HTTP ERROR", apiResponse.status, responseText);
      redirectToLogin(
        "backend_http_error",
        ssoSession.userId,
        ssoSession.userIc
      );
    }

    try {

      authResult = JSON.parse(responseText);

    } catch (jsonError) {
      console.error("[NEXT.JS] FASTAPI RETURNED INVALID JSON", responseText);
      redirectToLogin(
        "backend_invalid_json",
        ssoSession.userId,
        ssoSession.userIc
      );
    }

    if (!authResult || typeof authResult !== "object") {
      redirectToLogin(
        "auth_data_error",
        ssoSession.userId,
        ssoSession.userIc
      );
    }

  } catch (error: any) {

    if (
      error?.digest &&
      String(error.digest).startsWith("NEXT_REDIRECT")
    ) {
      throw error;
    }

    redirectToLogin(
      "backend_unexpected_error",
      ssoSession.userId,
      ssoSession.userIc
    );
  }


  // ============================================================
  // 3. PROCESS AUTHORIZATION RESULT
  // ============================================================

  // ============================================================
  // 3. PROCESS AUTHORIZATION RESULT (UPDATED LOGIC)
  // ============================================================

  const resolvedName = encodeRedirectValue(
    authResult.name || ssoSession.userId
  );

  const resolvedEmpNo = encodeRedirectValue(
    authResult.empNo || ssoSession.userIc
  );

  const resolvedEmail = encodeRedirectValue(
    authResult.email || "No Email Provided"
  );

  // Check if the database confirmed a match for at least ONE of the identifiers
  const isUserIdMatch = authResult.userIdMatch === true; // Or whatever property your FastAPI returns
  const isUserIcMatch = authResult.userIcMatch === true;

  // Fallback to strict check if individual match flags aren't returned by FastAPI,
  // or use your custom either/or boolean condition provided by the backend:
  const hasEitherMatch = authResult.eitherMatch === true || (isUserIdMatch || isUserIcMatch);

  if (
    authResult.user_state === "not exist" &&
    authResult.authority === "not exist"
  ) {
    redirect(
      `/login?error=not_exist` +
      `&userId=${resolvedName}` +
      `&userIc=${resolvedEmpNo}` +
      `&email=${resolvedEmail}`
    );
  }

  // Update condition: only reject if NEITHER matches (instead of strict mutual failure)
  if (!hasEitherMatch && authResult.auth === "no") {
    redirect(
      `/login?error=no_auth` +
      `&userId=${resolvedName}` +
      `&userIc=${resolvedEmpNo}` +
      `&email=${resolvedEmail}`
    );
  }


  // ============================================================
  // 4. LOAD POSTGRES DATA
  // ============================================================

  try {

    const result = await pool.query(
      "SELECT * FROM resultmain"
    );

    const mappedResultData = result.rows.map(
      (row: any, index: number) => ({

        id: row.id || index,

        mpModel: row["mp model"] || row.mp_model || "",

        devModel: row["dev model"] || row.dev_model || "",

        initialModel: row["initial model"] || row.initial_model || "",

        // Crosscheck Configuration (kolom baru di resultmain, ditambahkan backend)
        initialRegion: row["initial region"] || row.initial_region || "",

        jiraPowerConsLink: row["jira power cons link"] || row.jira_power_cons_link || "",

        result: row.result || "",

        structure: row.structure || "",

        benComp: row.benComp || row.bencomp || "",

        hwTool: row.hwTool || row.hwtool || "",

        substituteCheck: row.substitute_check || "",

        toolOption: row.tool_option || "",

        operationPlan: row.operation_plan || "",

        compareNote: row.compare_note || "",

        year: row.year || "",

        version: row.version || "",

        modelCircuitPic: row.model_circuit_pic || "",

        modelSubsidiary: row.model_subsidiary || "",

        modelSeries: row.model_series || "",

        modelRegion: row.model_region || "",

        modelSoc: row.model_soc || "",

        engineerConfirmation: row.engineer_confirmation || "",

        bomReleaseDate:
          row.bom_release_date instanceof Date
            ? row.bom_release_date.toISOString().split("T")[0]
            : (row.bom_release_date || ""),

        bomDelayCount: row.bom_delay_count || 0,

        bomTeam: row.bom_team || "",

        remark: row.remark || "",

        additionalRemark: row.addtional_remark || row.additional_remark || "",
      })
    );

    return (
      <DashboardLayoutClient
        initialBomData={mappedResultData}

        ssoUser={{
          userId: ssoSession.userId || null,

          userIc: ssoSession.userIc || null,

          userName: authResult.userName || null,

          ssolgenet: ssoSession.ssolgenet || null,
        }}
      />
    );

  } catch (error: any) {

    if (
      error?.digest &&
      String(error.digest).startsWith("NEXT_REDIRECT")
    ) {
      throw error;
    }

    redirectToLogin(
      "database_error",
      ssoSession.userId,
      ssoSession.userIc
    );
  }
}