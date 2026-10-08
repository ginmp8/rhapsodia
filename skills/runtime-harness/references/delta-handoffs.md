# Incremental handoff transport

The existing runtime-handoff-v1 remains canonical transport content; domain handoffs are
unchanged. A new runtime-handoff-transport/v1 envelope carries either a complete receipt
or a delta over one retained exact parent. Neither form carries execution authority.

`handoff-delta --input <JSON>` takes target_id and optionally parent_id,
receiver_parent_id and parent_depth (0..8). The receiver's acknowledgement must equal the
retained parent ID. Both receipts must belong to the same workspace scope and task.
Missing parent, missing acknowledgement, different scope/task, depth 8, or a delta not
smaller than the full envelope selects full transport and resets depth to zero.

Delta fields: parent_id, target_id, changed, removed, depth, transport_id. Only next_action,
snapshot_id, pins and summary can change; only optional summary can be removed. Scope,
task identity and required field deletion cannot be patched. The resulting complete
receipt must hash to target_id; the transport itself is independently content-bound.

`handoff-apply --input <JSON>` takes transport and the exact parent_id for delta mode.
It reads but does not write the retained parent, validates transport and resulting full
receipt, rejects cross-scope data, and returns the reconstructed complete v1 receipt.
If the receiver no longer has the parent, request full transport; never guess its contents.

Decoding validates transport integrity only, not current source pins. The authorized
receiver may save the returned receipt and use `handoff-resume --input <FILE>` to recheck
live resources before use. Use the existing explicit --rebind workflow for foreign
workspaces. Keep each complete receipt; parent_depth is declared transport metadata,
not a durable execution log. There is no recursive chain traversal or workflow replay.
