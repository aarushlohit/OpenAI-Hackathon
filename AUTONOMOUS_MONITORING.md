# Autonomous Monitoring

Hermes-X autonomous monitoring watches known threat entities and emits operational events without changing the investigation engine.

Components:

- `AutonomousMonitorEngine`: coordinates watch checks, feed updates, and escalation.
- `EntityWatcher`: checks threat memory for monitored entities.
- `EscalationRules`: converts repeated entity reuse into escalation events.
- `MonitorScheduler`: supports one-shot and periodic monitoring tasks.

Events:

- `threat_feed_update`
- `recurring_pattern_detected`
- `escalation_triggered`
- `coordinated_attack_detected`

Monitoring targets include suspicious domains, Telegram handles, recruiter emails, UPI IDs, payment wallets, and recurring scam structures.

