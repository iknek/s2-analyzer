import asyncio
import datetime
import logging
import time
from typing import TYPE_CHECKING

from s2_analyzer_backend.cem_model_simple.device_model import DeviceModel
from s2_analyzer_backend.model import Model

if TYPE_CHECKING:
    from s2_analyzer_backend.connection import Connection, ConnectionClosedReason
    from s2_analyzer_backend.envelope import Envelope
    from s2_analyzer_backend.router import MessageRouter

LOGGER = logging.getLogger(__name__)


class CEM(Model):
    SCHEDULE_INTERVAL = datetime.timedelta(minutes=1)

    message_router: 'MessageRouter'
    device_models_by_rm_ids: dict[str, DeviceModel]

    def __init__(self, id: str, message_router: 'MessageRouter'):
        super().__init__(id, message_router)
        self.message_router = message_router
        self.device_models_by_rm_ids = {}

    async def receive_envelope(self, envelope: 'Envelope') -> None:
        device_model = self.device_models_by_rm_ids.get(envelope.origin.origin_id)

        if not device_model:
            LOGGER.error(f'Received a message from {envelope.origin} but this connection is unknown to CEM '
                         f'model {self.id}.')
        else:
            LOGGER.debug(f'Received message {envelope.id} with type {envelope.msg_type} from {envelope.origin} for '
                         f'device {device_model.id}')
            await device_model.receive_envelope(envelope)

    def receive_new_connection(self, new_connection: 'Connection') -> bool:
        """

        :param new_connection: The new model connection with this CEM model as origin and the RM as destination.
        :return:
        """
        if new_connection.destination_type.isRM():
            LOGGER.info(f'CEM model {self.id} has received new connection from RM {new_connection.dest_id}.')
            device_model_id = f'{self.id}->{new_connection.dest_id}'
            self.device_models_by_rm_ids[new_connection.dest_id] = DeviceModel(device_model_id,
                                                                               new_connection,
                                                                               self.message_router)
            accepted = True
        else:
            LOGGER.warning(f'CEM model {self.id} has received a CEM->CEM model connection '
                           f'(CEM: {new_connection.dest_id}).'
                           f'CEM to CEM connection is unsupported. Not accepting connection.')
            accepted = False

        return accepted

    def connection_has_closed(self, closed_connection: 'Connection', reason: 'ConnectionClosedReason') -> None:
        if closed_connection.dest_id in self.device_models_by_rm_ids:
            del self.device_models_by_rm_ids[closed_connection.dest_id]
            LOGGER.info(f'CEM model {self.id} was notified that connection '
                        f'from {closed_connection.dest_id} was closed due to {reason}.')
        else:
            LOGGER.warning(f'CEM model {self.id} was notified that unknown '
                           f'connection {closed_connection.dest_id} was closed. Not doing anything...')

    async def entry(self) -> None:
        """Progress all device models each timestep."""
        timestep_start = datetime.datetime.now()
        timestep_end = timestep_start + CEM.SCHEDULE_INTERVAL

        while self._running:
            for device_model in self.device_models_by_rm_ids.values():
                new_messages = device_model.tick(timestep_start, timestep_end)

                for new_message in new_messages:
                    await self.message_router.route_s2_message(device_model.model_connection_to_rm, new_message)

            delay = timestep_end.timestamp() - time.time()
            if delay > 0:
                LOGGER.debug(f'CEM model {self.id} will sleep for {delay} seconds until {timestep_end}.')
                await asyncio.sleep(delay)
            timestep_start = datetime.datetime.now()
            timestep_end = timestep_start + CEM.SCHEDULE_INTERVAL
