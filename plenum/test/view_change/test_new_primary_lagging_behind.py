import pytest

from plenum.test.delayers import pDelay, cDelay
from plenum.test.helper import sdk_send_random_and_check, checkViewNoForNodes
from plenum.test.node_request.helper import sdk_ensure_pool_functional
from plenum.test.stasher import delay_rules_without_processing, delay_rules
from plenum.test.test_node import ensureElectionsDone
from plenum.test.view_change.helper import ensure_view_change
from plenum.test.view_change_service.helper import get_next_primary_name


CHK_FREQ = 5


@pytest.fixture(scope="module")
def tconf(tconf):
    old_chk = tconf.CHK_FREQ
    old_log_size = tconf.LOG_SIZE
    old_b_size = tconf.Max3PCBatchSize
    tconf.CHK_FREQ = CHK_FREQ
    tconf.LOG_SIZE = CHK_FREQ * 3
    tconf.Max3PCBatchSize = 1

    yield tconf
    tconf.CHK_FREQ = old_chk
    tconf.LOG_SIZE = old_log_size
    tconf.Max3PCBatchSize = old_b_size


def test_new_primary_lagging_behind(looper,
                                    txnPoolNodeSet,
                                    sdk_wallet_client,
                                    sdk_pool_handle,
                                    tconf):
    initial_view_no = checkViewNoForNodes(txnPoolNodeSet)
    next_primary_name = get_next_primary_name(txnPoolNodeSet, initial_view_no + 1)
    next_primary = [n for n in txnPoolNodeSet if n.name == next_primary_name][0]
    expected_primary_name = get_next_primary_name(txnPoolNodeSet, initial_view_no + 2)
    # Next primary cannot stabilize 1 checkpoint
    with delay_rules(next_primary.nodeIbStasher, cDelay(), pDelay()):
        sdk_send_random_and_check(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_client, CHK_FREQ)
        ensure_view_change(looper, txnPoolNodeSet)
    ensureElectionsDone(looper=looper, nodes=txnPoolNodeSet,
                        customTimeout=2 * tconf.NEW_VIEW_TIMEOUT)

    assert next_primary_name != expected_primary_name
    assert checkViewNoForNodes(txnPoolNodeSet) == initial_view_no + 2
    sdk_ensure_pool_functional(looper, txnPoolNodeSet, sdk_wallet_client, sdk_pool_handle)
