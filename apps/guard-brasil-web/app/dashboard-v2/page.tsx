import { redirect } from 'next/navigation';

// V2 merged into V1 (Activity Feed tab covers this use case)
export default function Page() {
  redirect('/dashboard-v1');
}
