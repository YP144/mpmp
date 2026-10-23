import { Pool } from 'pg';

const poolAuto = new Pool({
  connectionString: "postgresql://mybini-user:vzS3Bo0K8Bx2DcHQPd0zIpkiEhjDcZKJ8vyTqHPcwF796dMbYF0m4dFaedWAxWIN@mybini-0.mybini.postgres.svc:5432/MasterMP_Auto",
  ssl: false,
});

export default poolAuto;