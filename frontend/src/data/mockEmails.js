export const interceptedEmails = [
  {
    id: "evt_9942a",
    sender: "security-alert@amaz0n-verify.com",
    subject: "URGENT: Your account has been compromised",
    body: "Dear User,\n\nWe detected unauthorized access. <span class='fraud-highlight'>Click here immediately</span> to secure your account.\n\n- Amazon Support",
    riskScore: 93,
    classification: "CRITICAL",
    campaignId: "cmp_alpha_01"
  },
  {
    id: "evt_9942b",
    sender: "it-admin@corp-portal.net",
    subject: "Mandatory Update Required",
    body: "All employees must install the <span class='fraud-highlight'>attached security patch</span> by EOD.",
    riskScore: 87,
    classification: "HIGH",
    campaignId: "cmp_alpha_01"
  },
  {
    id: "evt_9942c",
    sender: "payroll@company-hr.biz",
    subject: "Payroll Update - Action Needed",
    body: "Please verify your direct deposit details by clicking the <span class='fraud-highlight'>secure link</span> below to avoid payment delays.",
    riskScore: 78,
    classification: "HIGH",
    campaignId: "cmp_beta_02"
  },
  {
    id: "evt_9942d",
    sender: "newsletter@tech-daily.com",
    subject: "Your Weekly Tech Digest",
    body: "Here's what happened this week in tech. No action required — just your regular newsletter.",
    riskScore: 12,
    classification: "LOW",
    campaignId: null
  }
];
