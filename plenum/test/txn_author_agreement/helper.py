from typing import NamedTuple, Dict

from indy.ledger import build_txn_author_agreement_request

from plenum.common.constants import (
    CONFIG_LEDGER_ID,
    TXN_AUTHOR_AGREEMENT_TEXT, TXN_AUTHOR_AGREEMENT_VERSION,
    TXN_PAYLOAD, TXN_METADATA, TXN_METADATA_SEQ_NO, TXN_METADATA_TIME
)
from plenum.common.util import randomString
from plenum.server.config_req_handler import ConfigReqHandler


TaaData = NamedTuple("TaaData", [
    ("version", str),
    ("text", str),
    ("seqNo", int),
    ("txnTime", int)
])


async def prepare_txn_author_agreement(did: str):
    text = randomString(1024)
    version = randomString(16)
    return await build_txn_author_agreement_request(did, text, version)


def get_config_req_handler(node):
    config_req_handler = node.get_req_handler(CONFIG_LEDGER_ID)
    assert isinstance(config_req_handler, ConfigReqHandler)
    return config_req_handler


def expected_state_data(data: TaaData) -> Dict:
    return {
        TXN_PAYLOAD: {
            TXN_AUTHOR_AGREEMENT_VERSION: data.version,
            TXN_AUTHOR_AGREEMENT_TEXT: data.text
        },
        TXN_METADATA: {
            TXN_METADATA_SEQ_NO: data.seqNo,
            TXN_METADATA_TIME: data.txnTime
        }
    }
