# Educational rules and limits

Ansible renders service ports from `config/lab.yml`. Every rule uses `$HOME_NET`
as its source and `$LAB_TARGET` as its destination. Both test source and target
are private, so using the usual `EXTERNAL_NET: !$HOME_NET` would miss the exercise.
The rules are compatible in intent with the Ubuntu Suricata 7 family; always run
the installed engine's `suricata -T` before starting it.

| SID | Event / signal | Expected exercise |
| --- | --- | --- |
| 1000001 | ICMP echo request | `simulate ping`, at most a handful of echo requests |
| 1000002 | Four SYN packets from a source within 20 seconds | `simulate discover`; retransmits also count |
| 1000003 | Three SSH SYN packets within 20 seconds | `simulate ssh` or `tcp`; does not establish failed authentication |
| 1000004 | URI starts with `/admin-test` | `simulate urls` |
| 1000005 | URI starts with `/security-test` | `simulate urls` |
| 1000006 | URI starts with `/scanner-test` | `simulate urls` |
| 1000007 | GET request frequency exceeds five matches in ten seconds | `simulate http --count 8` |
| 1000008 | Unexpected SYN+FIN flag combination | No live generator supplied; review-only signature |

Thresholds are deliberately small for a controlled classroom example. Rules 2
and 3 use `type threshold` and alert on the counted match, then reset. Rule 7
uses `detection_filter`, which begins alerting after the count is exceeded.
These are packet/transaction counts, not counts of distinct ports or successful
logins. Ordinary troubleshooting can trigger them. Marker rules also match
suffixes because they use `startswith`; they are telemetry markers, not exploit
signatures. Do not interpret them as evidence of compromise.

Classification priority is not an incident severity verdict. Document evidence,
context and uncertainty in the incident report. See
[Suricata 7 threshold semantics](https://docs.suricata.io/en/suricata-7.0.10/rules/thresholding.html)
and [HTTP keywords](https://docs.suricata.io/en/suricata-7.0.10/rules/http-keywords.html).
