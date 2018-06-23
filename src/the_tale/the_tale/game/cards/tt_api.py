
import smart_imports

smart_imports.all()


def change_cards(account_id, operation_type, to_add=(), to_remove=(), storage=relations.STORAGE.FAST):
    operations = []

    for card in to_remove:
        operations.append(storage_pb2.Operation(destroy=storage_pb2.OperationDestroy(item_id=card.uid.hex,
                                                                                     owner_id=account_id,
                                                                                     operation_type=operation_type)))

    for card in to_add:
        operations.append(storage_pb2.Operation(create=storage_pb2.OperationCreate(item_id=card.uid.hex,
                                                                                   owner_id=account_id,
                                                                                   storage_id=storage.value,
                                                                                   base_type=card.item_base_type,
                                                                                   full_type=card.item_full_type,
                                                                                   data=s11n.to_json(card.serialize()),
                                                                                   operation_type=operation_type)))

    utils_tt_api.sync_request(url=conf.settings.TT_STORAGE_APPLY_URL,
                        data=storage_pb2.ApplyRequest(operations=operations),
                        AnswerType=storage_pb2.ApplyResponse)


def change_cards_owner(old_owner_id, new_owner_id, operation_type, new_storage, cards_ids):
    operations = []

    for card_id in cards_ids:
        operations.append(storage_pb2.Operation(change_owner=storage_pb2.OperationChangeOwner(item_id=card_id.hex,
                                                                                              old_owner_id=old_owner_id,
                                                                                              new_owner_id=new_owner_id,
                                                                                              new_storage_id=new_storage.value,
                                                                                              operation_type=operation_type)))

    utils_tt_api.sync_request(url=conf.settings.TT_STORAGE_APPLY_URL,
                        data=storage_pb2.ApplyRequest(operations=operations),
                        AnswerType=storage_pb2.ApplyResponse)


def change_cards_storage(account_id, operation_type, cards, old_storage, new_storage):
    operations = []

    for card in cards:
        operations.append(storage_pb2.Operation(change_storage=storage_pb2.OperationChangeStorage(item_id=card.uid.hex,
                                                                                                  owner_id=account_id,
                                                                                                  old_storage_id=old_storage.value,
                                                                                                  new_storage_id=new_storage.value,
                                                                                                  operation_type=operation_type)))

    utils_tt_api.sync_request(url=conf.settings.TT_STORAGE_APPLY_URL,
                        data=storage_pb2.ApplyRequest(operations=operations),
                        AnswerType=storage_pb2.ApplyResponse)


def load_cards(account_id):
    answer = utils_tt_api.sync_request(url=conf.settings.TT_STORAGE_GET_ITEMS_URL,
                                 data=storage_pb2.GetItemsRequest(owner_id=account_id),
                                 AnswerType=storage_pb2.GetItemsResponse)

    cards = {}

    for item in answer.items:
        id = uuid.UUID(item.id)
        cards[id] = objects.Card.deserialize(uid=id,
                                             data=s11n.from_json(item.data),
                                             storage=relations.STORAGE(item.storage_id))

    return cards


def has_cards(account_id, cards_ids):
    answer = utils_tt_api.sync_request(url=conf.settings.TT_STORAGE_HAS_ITEMS_URL,
                                 data=storage_pb2.HasItemsRequest(owner_id=account_id, items_ids=[id.hex for id in cards_ids]),
                                 AnswerType=storage_pb2.HasItemsResponse)
    return answer.has


def debug_clear_service():
    if not django_settings.TESTS_RUNNING:
        return

    utils_tt_api.sync_request(url=conf.settings.TT_STORAGE_DEBUG_CLEAR_SERVICE_URL,
                        data=storage_pb2.DebugClearServiceRequest(),
                        AnswerType=storage_pb2.DebugClearServiceResponse)
