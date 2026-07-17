import type { Metadata } from "next";
import { LoanApplicationForm } from "@/components/customer/LoanApplicationForm";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";

export const metadata: Metadata = { title: "Apply for a loan" };

export default function ApplyPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Apply for a loan</CardTitle>
          <CardDescription>
            Takes about two minutes. Your default-risk prediction appears the moment you submit.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LoanApplicationForm />
        </CardContent>
      </Card>
    </div>
  );
}