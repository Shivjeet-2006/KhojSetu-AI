# Secure claim and owner-verification workflow

## Current limitation

The current application stores lost/found report details in a Supabase `reports`
table. The application code does not implement user sign-in, owner identity,
owner contact storage, or authenticated ownership of a report. Therefore, a
public form that asks a question and immediately reveals contact information
would not be a secure claim workflow.

## Recommended production design

1. Add Supabase Auth (email OTP or another verified sign-in method).
2. Add an `owner_id uuid references auth.users(id)` column to reports.
   New reports must be created only for the signed-in user.
3. Keep owner contact details in a private profile table, not in the public
   reports query or public report cards.
4. Add a `claim_requests` table with report ID, claimant user ID, a short
   claim explanation, status, timestamps, and an owner response.
5. Enable Row Level Security on both tables. Owners may read claims only for
   reports they own; claimants may read only their own submitted claims.
   Public/anonymous users must not be able to select claim rows or owner data.
6. Submit claims through a server-side function or authenticated database
   policy. Validate report ownership and status server-side, rate-limit
   repeated requests, and record an audit trail.
7. Let the owner review the claimant's private identifying details and approve
   or reject the claim. Reveal contact details only after an explicit approval
   and only to the verified parties.
8. Never use a public "secret question" as the sole authorization mechanism.
   Answers can be guessed, copied from public posts, or brute-forced.

## Required before enabling the live claim UI

- Confirm whether Supabase Auth is enabled in the project.
- Review the actual Supabase table schema and existing RLS policies in the
  Supabase dashboard. These are not present in this GitHub repository.
- Decide whether owners will sign in with email OTP.
- Add and test the SQL migration and authenticated server-side operations.
- Test that anonymous users cannot read claims, owner contact details, or
  another user's private information.

Until these steps are completed, the app should continue to show public item
descriptions only and must not reveal owner contact details.
