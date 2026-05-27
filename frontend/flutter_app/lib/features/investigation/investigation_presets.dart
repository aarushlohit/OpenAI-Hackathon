class InvestigationPreset {
  const InvestigationPreset({required this.name, required this.input});

  final String name;
  final String input;
}

const investigationPresets = [
  InvestigationPreset(
    name: 'Telegram onboarding scam',
    input: 'Telegram HR from @careerfastjob claims direct internship selection. '
        'Asks refundable onboarding payment of 3500. Provides UPI pay@upi. '
        'Sends URL: https://career-fasttrack-placement.xyz. Claims limited slots.',
  ),
  InvestigationPreset(
    name: 'Fake internship portal',
    input: 'Verify internship onboarding at https://new-careers.xyz/verify before interview. '
        'Recruiter claims direct selection and Telegram-only communication.',
  ),
  InvestigationPreset(
    name: 'Forged offer letter',
    input: 'Offer letter requires refundable security deposit before joining confirmation '
        'and bypasses interview process.',
  ),
  InvestigationPreset(
    name: 'Recruiter impersonation',
    input: 'Recruiter using hr@career-fasttrack-placement.xyz asks for documents and '
        'sends Telegram handle @careerfastjob for onboarding payment.',
  ),
  InvestigationPreset(
    name: 'Coordinated campaign',
    input: 'Multiple domains reuse @careerfastjob and pay@upi across cloned internship '
        'portals with limited slot pressure.',
  ),
];

