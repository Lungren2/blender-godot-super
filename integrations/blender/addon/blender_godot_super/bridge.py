"""Blender-side transport and dispatch scaffold.

No socket or RPC implementation lives here yet. The first implementation must
define lifecycle, locality/authentication, cancellation, timeout, and main-thread
dispatch semantics before transport code is added.
"""
