(define (problem hyptest-test20-s3-90-s9)
 (:domain appn-pls)
 (:init (breaker-state-is-unknown_breaker_x1_x2) (breaker-state-is-unknown_breaker_x3_x4) (breaker-state-is-unknown_breaker_x5_x6) (breaker-state-is-unknown_breaker_x7_x8) (breaker-state-is-unknown_breaker_x9_x10) (breaker-state-is-unknown_breaker_x11_x12) (breaker-state-is-unknown_breaker_x15_x16) (breaker-state-is-unknown_breaker_x17_x18) (breaker-state-is-unknown_breaker_x19_x20) (breaker-state-is-unknown_breaker_x21_x22) (breaker-state-is-unknown_breaker_x23_x24) (breaker-state-is-unknown_breaker_x25_x26) (breaker-state-is-unknown_breaker_x29_x30) (breaker-state-is-unknown_breaker_x31_x32) (breaker-state-is-unknown_breaker_x37_x38) (breaker-state-is-unknown_breaker_x39_x40) (breaker-state-is-unknown_breaker_x41_x42) (breaker-state-is-unknown_breaker_x49_x50) (breaker-state-is-unknown_breaker_x53_x54) (breaker-state-is-unknown_breaker_x55_x56) (breaker-state-is-unknown_breaker_x57_x58) (breaker-state-is-unknown_breaker_x59_x60) (breaker-state-is-unknown_breaker_x61_x62) (breaker-ar-status-is-unknown_breaker_x1_x2) (breaker-ar-status-is-unknown_breaker_x3_x4) (breaker-ar-status-is-unknown_breaker_x5_x6) (breaker-ar-status-is-unknown_breaker_x7_x8) (breaker-ar-status-is-unknown_breaker_x9_x10) (breaker-ar-status-is-unknown_breaker_x11_x12) (breaker-ar-status-is-unknown_breaker_x15_x16) (breaker-ar-status-is-unknown_breaker_x21_x22) (breaker-ar-status-is-unknown_breaker_x23_x24) (breaker-ar-status-is-unknown_breaker_x25_x26) (breaker-ar-status-is-unknown_breaker_x29_x30) (breaker-ar-status-is-unknown_breaker_x31_x32) (fault-count-2_count-as-fault_breaker_x1_x2_n0) (dominates-2_hyp15_count-as-fault_breaker_x1_x2) (dominates-2_hyp14_count-as-fault_breaker_x1_x2) (dominates-2_hyp13_count-as-fault_breaker_x1_x2) (dominates-2_hyp12_count-as-fault_breaker_x1_x2) (dominates-2_hyp11_count-as-fault_breaker_x1_x2) (dominates-2_hyp10_count-as-fault_breaker_x1_x2) (dominates-2_hyp9_count-as-fault_breaker_x1_x2) (dominates-2_hyp8_count-as-fault_breaker_x1_x2) (dominates-2_hyp7_count-as-fault_breaker_x1_x2) (dominates-2_hyp6_count-as-fault_breaker_x1_x2) (dominates-2_hyp5_count-as-fault_breaker_x1_x2) (dominates-2_hyp4_count-as-fault_breaker_x1_x2) (dominates-2_hyp3_count-as-fault_breaker_x1_x2) (dominates-2_hyp2_count-as-fault_breaker_x1_x2) (dominates-2_hyp1_count-as-fault_breaker_x1_x2) (fault-count-2_count-as-fault_breaker_x3_x4_n0) (dominates-2_hyp15_count-as-fault_breaker_x3_x4) (dominates-2_hyp14_count-as-fault_breaker_x3_x4) (dominates-2_hyp13_count-as-fault_breaker_x3_x4) (dominates-2_hyp12_count-as-fault_breaker_x3_x4) (dominates-2_hyp11_count-as-fault_breaker_x3_x4) (dominates-2_hyp10_count-as-fault_breaker_x3_x4) (dominates-2_hyp9_count-as-fault_breaker_x3_x4) (dominates-2_hyp8_count-as-fault_breaker_x3_x4) (dominates-2_hyp7_count-as-fault_breaker_x3_x4) (dominates-2_hyp6_count-as-fault_breaker_x3_x4) (dominates-2_hyp5_count-as-fault_breaker_x3_x4) (dominates-2_hyp4_count-as-fault_breaker_x3_x4) (dominates-2_hyp3_count-as-fault_breaker_x3_x4) (dominates-2_hyp2_count-as-fault_breaker_x3_x4) (dominates-2_hyp1_count-as-fault_breaker_x3_x4) (fault-count-2_count-as-fault_breaker_x5_x6_n0) (dominates-2_hyp15_count-as-fault_breaker_x5_x6) (dominates-2_hyp14_count-as-fault_breaker_x5_x6) (dominates-2_hyp13_count-as-fault_breaker_x5_x6) (dominates-2_hyp12_count-as-fault_breaker_x5_x6) (dominates-2_hyp11_count-as-fault_breaker_x5_x6) (dominates-2_hyp10_count-as-fault_breaker_x5_x6) (dominates-2_hyp9_count-as-fault_breaker_x5_x6) (dominates-2_hyp8_count-as-fault_breaker_x5_x6) (dominates-2_hyp7_count-as-fault_breaker_x5_x6) (dominates-2_hyp6_count-as-fault_breaker_x5_x6) (dominates-2_hyp5_count-as-fault_breaker_x5_x6) (dominates-2_hyp4_count-as-fault_breaker_x5_x6) (dominates-2_hyp3_count-as-fault_breaker_x5_x6) (dominates-2_hyp2_count-as-fault_breaker_x5_x6) (dominates-2_hyp1_count-as-fault_breaker_x5_x6) (fault-count-2_count-as-fault_breaker_x7_x8_n0) (dominates-2_hyp15_count-as-fault_breaker_x7_x8) (dominates-2_hyp12_count-as-fault_breaker_x7_x8) (dominates-2_hyp10_count-as-fault_breaker_x7_x8) (dominates-2_hyp8_count-as-fault_breaker_x7_x8) (dominates-2_hyp6_count-as-fault_breaker_x7_x8) (dominates-2_hyp3_count-as-fault_breaker_x7_x8) (dominates-2_hyp2_count-as-fault_breaker_x7_x8) (fault-count-2_count-as-fault_breaker_x9_x10_n0) (dominates-2_hyp15_count-as-fault_breaker_x9_x10) (dominates-2_hyp14_count-as-fault_breaker_x9_x10) (dominates-2_hyp13_count-as-fault_breaker_x9_x10) (dominates-2_hyp12_count-as-fault_breaker_x9_x10) (dominates-2_hyp8_count-as-fault_breaker_x9_x10) (dominates-2_hyp7_count-as-fault_breaker_x9_x10) (dominates-2_hyp6_count-as-fault_breaker_x9_x10) (dominates-2_hyp5_count-as-fault_breaker_x9_x10) (fault-count-2_count-as-fault_breaker_x11_x12_n0) (dominates-2_hyp15_count-as-fault_breaker_x11_x12) (dominates-2_hyp14_count-as-fault_breaker_x11_x12) (dominates-2_hyp13_count-as-fault_breaker_x11_x12) (dominates-2_hyp12_count-as-fault_breaker_x11_x12) (dominates-2_hyp11_count-as-fault_breaker_x11_x12) (dominates-2_hyp10_count-as-fault_breaker_x11_x12) (dominates-2_hyp9_count-as-fault_breaker_x11_x12) (fault-count-2_count-as-fault_breaker_x15_x16_n0) (fault-count-2_count-as-fault_breaker_x21_x22_n0) (dominates-2_hyp15_count-as-fault_breaker_x21_x22) (dominates-2_hyp14_count-as-fault_breaker_x21_x22) (dominates-2_hyp13_count-as-fault_breaker_x21_x22) (dominates-2_hyp12_count-as-fault_breaker_x21_x22) (dominates-2_hyp11_count-as-fault_breaker_x21_x22) (dominates-2_hyp10_count-as-fault_breaker_x21_x22) (dominates-2_hyp9_count-as-fault_breaker_x21_x22) (fault-count-2_count-as-fault_breaker_x23_x24_n0) (dominates-2_hyp15_count-as-fault_breaker_x23_x24) (dominates-2_hyp14_count-as-fault_breaker_x23_x24) (dominates-2_hyp13_count-as-fault_breaker_x23_x24) (dominates-2_hyp12_count-as-fault_breaker_x23_x24) (dominates-2_hyp11_count-as-fault_breaker_x23_x24) (dominates-2_hyp10_count-as-fault_breaker_x23_x24) (dominates-2_hyp9_count-as-fault_breaker_x23_x24) (fault-count-2_count-as-fault_breaker_x25_x26_n0) (dominates-2_hyp15_count-as-fault_breaker_x25_x26) (dominates-2_hyp14_count-as-fault_breaker_x25_x26) (dominates-2_hyp13_count-as-fault_breaker_x25_x26) (dominates-2_hyp12_count-as-fault_breaker_x25_x26) (dominates-2_hyp11_count-as-fault_breaker_x25_x26) (dominates-2_hyp10_count-as-fault_breaker_x25_x26) (dominates-2_hyp9_count-as-fault_breaker_x25_x26) (dominates-2_hyp8_count-as-fault_breaker_x25_x26) (dominates-2_hyp7_count-as-fault_breaker_x25_x26) (dominates-2_hyp6_count-as-fault_breaker_x25_x26) (dominates-2_hyp5_count-as-fault_breaker_x25_x26) (dominates-2_hyp4_count-as-fault_breaker_x25_x26) (dominates-2_hyp3_count-as-fault_breaker_x25_x26) (dominates-2_hyp2_count-as-fault_breaker_x25_x26) (dominates-2_hyp1_count-as-fault_breaker_x25_x26) (fault-count-2_count-as-fault_breaker_x29_x30_n0) (dominates-2_hyp13_count-as-fault_breaker_x29_x30) (dominates-2_hyp12_count-as-fault_breaker_x29_x30) (dominates-2_hyp9_count-as-fault_breaker_x29_x30) (dominates-2_hyp6_count-as-fault_breaker_x29_x30) (dominates-2_hyp5_count-as-fault_breaker_x29_x30) (dominates-2_hyp2_count-as-fault_breaker_x29_x30) (dominates-2_hyp1_count-as-fault_breaker_x29_x30) (fault-count-2_count-as-fault_breaker_x31_x32_n0) (dominates-2_hyp15_count-as-fault_breaker_x31_x32) (dominates-2_hyp14_count-as-fault_breaker_x31_x32) (dominates-2_hyp13_count-as-fault_breaker_x31_x32) (dominates-2_hyp12_count-as-fault_breaker_x31_x32) (dominates-2_hyp8_count-as-fault_breaker_x31_x32) (dominates-2_hyp7_count-as-fault_breaker_x31_x32) (dominates-2_hyp6_count-as-fault_breaker_x31_x32) (dominates-2_hyp5_count-as-fault_breaker_x31_x32) (fault-count-2_count-as-fault_breaker_x17_x18_n0) (dominates-2_hyp15_count-as-fault_breaker_x17_x18) (dominates-2_hyp14_count-as-fault_breaker_x17_x18) (dominates-2_hyp13_count-as-fault_breaker_x17_x18) (dominates-2_hyp12_count-as-fault_breaker_x17_x18) (dominates-2_hyp11_count-as-fault_breaker_x17_x18) (dominates-2_hyp10_count-as-fault_breaker_x17_x18) (dominates-2_hyp9_count-as-fault_breaker_x17_x18) (dominates-2_hyp8_count-as-fault_breaker_x17_x18) (dominates-2_hyp7_count-as-fault_breaker_x17_x18) (dominates-2_hyp6_count-as-fault_breaker_x17_x18) (dominates-2_hyp5_count-as-fault_breaker_x17_x18) (dominates-2_hyp4_count-as-fault_breaker_x17_x18) (dominates-2_hyp3_count-as-fault_breaker_x17_x18) (dominates-2_hyp2_count-as-fault_breaker_x17_x18) (dominates-2_hyp1_count-as-fault_breaker_x17_x18) (fault-count-2_count-as-fault_breaker_x19_x20_n0) (dominates-2_hyp15_count-as-fault_breaker_x19_x20) (dominates-2_hyp14_count-as-fault_breaker_x19_x20) (dominates-2_hyp13_count-as-fault_breaker_x19_x20) (dominates-2_hyp12_count-as-fault_breaker_x19_x20) (dominates-2_hyp11_count-as-fault_breaker_x19_x20) (dominates-2_hyp10_count-as-fault_breaker_x19_x20) (dominates-2_hyp9_count-as-fault_breaker_x19_x20) (dominates-2_hyp8_count-as-fault_breaker_x19_x20) (dominates-2_hyp7_count-as-fault_breaker_x19_x20) (dominates-2_hyp6_count-as-fault_breaker_x19_x20) (dominates-2_hyp5_count-as-fault_breaker_x19_x20) (dominates-2_hyp4_count-as-fault_breaker_x19_x20) (dominates-2_hyp3_count-as-fault_breaker_x19_x20) (dominates-2_hyp2_count-as-fault_breaker_x19_x20) (dominates-2_hyp1_count-as-fault_breaker_x19_x20) (pending_obs1680) (fault-count-2_count-as-fault_bus_x33_n0) (dominates-2_hyp15_count-as-fault_bus_x33) (dominates-2_hyp14_count-as-fault_bus_x33) (dominates-2_hyp13_count-as-fault_bus_x33) (dominates-2_hyp12_count-as-fault_bus_x33) (dominates-2_hyp11_count-as-fault_bus_x33) (dominates-2_hyp10_count-as-fault_bus_x33) (dominates-2_hyp9_count-as-fault_bus_x33) (dominates-2_hyp8_count-as-fault_bus_x33) (dominates-2_hyp7_count-as-fault_bus_x33) (dominates-2_hyp6_count-as-fault_bus_x33) (dominates-2_hyp5_count-as-fault_bus_x33) (dominates-2_hyp4_count-as-fault_bus_x33) (dominates-2_hyp3_count-as-fault_bus_x33) (dominates-2_hyp2_count-as-fault_bus_x33) (dominates-2_hyp1_count-as-fault_bus_x33) (fault-count-2_count-as-fault_bus_x34_n0) (dominates-2_hyp15_count-as-fault_bus_x34) (dominates-2_hyp14_count-as-fault_bus_x34) (dominates-2_hyp13_count-as-fault_bus_x34) (dominates-2_hyp12_count-as-fault_bus_x34) (dominates-2_hyp11_count-as-fault_bus_x34) (dominates-2_hyp10_count-as-fault_bus_x34) (dominates-2_hyp9_count-as-fault_bus_x34) (dominates-2_hyp8_count-as-fault_bus_x34) (dominates-2_hyp7_count-as-fault_bus_x34) (dominates-2_hyp6_count-as-fault_bus_x34) (dominates-2_hyp5_count-as-fault_bus_x34) (dominates-2_hyp4_count-as-fault_bus_x34) (dominates-2_hyp3_count-as-fault_bus_x34) (dominates-2_hyp2_count-as-fault_bus_x34) (dominates-2_hyp1_count-as-fault_bus_x34) (fault-count-2_count-as-fault_line_x13_x14_n0) (not_line-isolated_line_x13_x14) (not_line-iso-trip-in-progress_line_x13_x14_obs1681) (fault-count-2_count-as-fault_line_x27_x28_n0) (not_line-isolated_line_x27_x28) (dominates-2_hyp15_count-as-fault_line_x27_x28) (dominates-2_hyp14_count-as-fault_line_x27_x28) (dominates-2_hyp11_count-as-fault_line_x27_x28) (dominates-2_hyp10_count-as-fault_line_x27_x28) (dominates-2_hyp8_count-as-fault_line_x27_x28) (dominates-2_hyp7_count-as-fault_line_x27_x28) (dominates-2_hyp4_count-as-fault_line_x27_x28) (dominates-2_hyp3_count-as-fault_line_x27_x28) (fault-count-2_count-as-fault_line_x35_x36_n0) (not_line-isolated_line_x35_x36) (dominates-2_hyp11_count-as-fault_line_x35_x36) (dominates-2_hyp10_count-as-fault_line_x35_x36) (dominates-2_hyp9_count-as-fault_line_x35_x36) (dominates-2_hyp4_count-as-fault_line_x35_x36) (dominates-2_hyp3_count-as-fault_line_x35_x36) (dominates-2_hyp2_count-as-fault_line_x35_x36) (dominates-2_hyp1_count-as-fault_line_x35_x36) (fault-count-2_count-as-fault_line_x43_x44_n0) (not_line-isolated_line_x43_x44) (dominates-2_hyp14_count-as-fault_line_x43_x44) (dominates-2_hyp13_count-as-fault_line_x43_x44) (dominates-2_hyp11_count-as-fault_line_x43_x44) (dominates-2_hyp9_count-as-fault_line_x43_x44) (dominates-2_hyp7_count-as-fault_line_x43_x44) (dominates-2_hyp5_count-as-fault_line_x43_x44) (dominates-2_hyp4_count-as-fault_line_x43_x44) (dominates-2_hyp1_count-as-fault_line_x43_x44) (fault-count-2_count-as-fault_line_x47_x48_n0) (not_line-isolated_line_x47_x48) (dominates-2_hyp8_count-as-fault_line_x47_x48) (dominates-2_hyp7_count-as-fault_line_x47_x48) (dominates-2_hyp6_count-as-fault_line_x47_x48) (dominates-2_hyp5_count-as-fault_line_x47_x48) (dominates-2_hyp4_count-as-fault_line_x47_x48) (dominates-2_hyp3_count-as-fault_line_x47_x48) (dominates-2_hyp2_count-as-fault_line_x47_x48) (dominates-2_hyp1_count-as-fault_line_x47_x48) (future_obs1681) (future_obs1682) (future_obs1683) (future_obs1684) (future_obs1685) (future_obs1686) (future_obs1687) (future_obs1688) (future_obs1689) (future_obs1690) (future_obs1691) (future_obs1692) (future_obs1693) (future_obs1694) (future_obs1695) (future_obs1696) (future_obs1697) (future_obs1698) (future_obs1699) (not_at_end_constraint0) (not_at_end_constraint1) (not_at_end_constraint2) (not_at_end_constraint3) (not_at_end_constraint4) (not_at_end_constraint5) (not_at_end_constraint6) (not_at_end_constraint7) (not_at_end_constraint8) (not_at_end_constraint9) (not_at_end_constraint10) (not_at_end_constraint11) (not_at_end_constraint12) (not_at_end_constraint13) (not_at_end_constraint14) (static-true))
 (:goal (and (observed_obs1699) (observed_obs1685) (observed_obs1697) (observed_obs1691) (observed_obs1689) (observed_obs1695) (observed_obs1681) (observed_obs1693) (observed_obs1690) (observed_obs1692) (observed_obs1694) (observed_obs1688) (observed_obs1696) (observed_obs1683) (observed_obs1680) (observed_obs1687) (observed_obs1682) (observed_obs1684) (observed_obs1698) (observed_obs1686) (achieved_constraint0) (achieved_constraint1) (achieved_constraint2) (achieved_constraint3) (achieved_constraint4) (achieved_constraint5) (achieved_constraint6) (achieved_constraint7) (achieved_constraint8) (achieved_constraint9) (achieved_constraint10) (achieved_constraint11) (achieved_constraint12) (achieved_constraint13) (achieved_constraint14)))
)
