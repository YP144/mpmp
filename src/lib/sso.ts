import { cookies } from 'next/headers';
import querystring from 'querystring';

export async function getSsoSession() {
  try {
    // Retrieve cookies from the incoming request (await is required in Next.js 15+)
    const cookieStore = await cookies();
    const ssolgenet = cookieStore.get('ssolgenet')?.value;
    const smsession = cookieStore.get('SMSESSION')?.value;

    if (!ssolgenet || !smsession) {
      return { success: false, error: 'SSO cookies not found' };
    }

    // Decode HTML entities (if any) and parse the query string
    const decodedSso = ssolgenet.replace(/&amp;/g, '&');
    const parsed = querystring.parse(decodedSso);
    
    const userId = parsed.empno as string;
    const userIc = parsed.ssoid as string;

    // Print values on every page load / request execution
    console.log('SSO Data:', {
      userId,
      userIc,
      ssolgenet
    });

    // Fetch the NPDM Bearer token
    const npdmResponse = await fetch('https://npdm.lge.com/api/foundation/user/login/sso?ssoRedirect=none', {
      method: 'POST',
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        // Inject the cookies into the request header
        'Cookie': `ssolgenet=${ssolgenet}; SMSESSION=${smsession}`,
        'Host': 'npdm.lge.com',
        'Origin': 'https://npdm.lge.com',
        'Referer': 'https://npdm.lge.com/ssoLogin'
      },
      body: JSON.stringify({ omfAuthenticationVO: { expiredHoursAfter: 18 } }),
      // Ensure we don't cache this request so it always checks the current session
      cache: 'no-store' 
    });

    const contentType = npdmResponse.headers.get('Content-Type') || '';

    if (npdmResponse.ok || contentType.includes('application/json')) {
      const jsonData = await npdmResponse.json();
      const authBearer = jsonData?.data?.token;

      return {
        success: true,
        userId,
        userIc,
        authBearer,
        smsession,
        ssolgenet
      };
    } else {
      return { success: false, error: 'NPDM Server not reachable or session expired' };
    }
  } catch (error) {
    console.error('Auto login failed:', error);
    return { success: false, error: 'An unexpected error occurred during SSO login' };
  }
}