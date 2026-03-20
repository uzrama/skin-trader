import asyncio
import logging
from typing import final

from skin_trader.configs.general import Settings
from skin_trader.exceptions.purchase_manager import PurchaseManagerError
from skin_trader.managers.purchase_processor import PurchaseProcessor
from skin_trader.schemas.purchase import PurchaseRequest

logger = logging.getLogger(__name__)


@final
class PurchaseWorker:
    """
    Manages a queue of purchase requests and processes them concurrently.

    This class is responsible for:
    - Maintaining a queue of purchase requests.
    - Starting and stopping a pool of worker tasks to process the requests.
    - Adding new purchase requests to the queue.

    Args:
        settings: The application settings.
        purchase_processor: The processor for handling individual purchase requests.
    """

    def __init__(self, settings: Settings, purchase_processor: PurchaseProcessor):
        self.purchase_processor = purchase_processor
        self.max_concurrent = settings.purchase_manager.max_concurrent
        self.is_running = False
        self.semaphore = asyncio.Semaphore(settings.purchase_manager.max_concurrent)
        self.purchase_queue: asyncio.Queue[PurchaseRequest] = asyncio.Queue(maxsize=settings.purchase_manager.max_queue)
        self.workers: list[asyncio.Task[None]] = []

    async def _worker(self):
        """The worker task that processes purchase requests from the queue."""
        while self.is_running:
            try:
                purchase_request = await asyncio.wait_for(self.purchase_queue.get(), timeout=1.0)
                try:
                    await self.purchase_processor.process_purchase(purchase_request)
                except Exception as e:
                    logger.error(f"Error processing '{purchase_request.name}': {e}")
                finally:
                    self.purchase_queue.task_done()
            except asyncio.TimeoutError:
                continue

    async def add_purchase(self, purchase_request: PurchaseRequest):
        """
        Adds a purchase request to the queue.

        Args:
            purchase_request: The purchase request to add to the queue.

        Raises:
            PurchaseManagerError: If the purchase manager is not running or the queue is full.
        """
        if not self.is_running:
            raise PurchaseManagerError("Purchase manager is not running")
        try:
            await self.purchase_queue.put(purchase_request)
            logger.debug(f"Purchase '{purchase_request.name}' added to queue")
        except asyncio.QueueFull:
            error_msg = f"Purchase queue is full, cannot add '{purchase_request.name}'"
            logger.error(error_msg)
            raise PurchaseManagerError(error_msg)

    async def start(self):
        """Starts the purchase manager and its worker tasks."""
        if self.is_running:
            logger.warning("Purchase manager is already running")
            return
        self.is_running = True
        self.workers = [asyncio.create_task(self._worker()) for _ in range(self.max_concurrent)]
        logger.info(f"Started {self.max_concurrent} workers")

    async def stop(self, wait_for_completion: bool = True):
        """
        Stops the purchase manager and its worker tasks.

        Args:
            wait_for_completion: If True, waits for all pending tasks to complete before stopping.
        """
        if not self.is_running:
            logger.warning("Purchase manager is not running")
            return

        self.is_running = False

        if wait_for_completion:
            await self.purchase_queue.join()
        for worker in self.workers:
            worker.cancel()

        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        logger.info("All workers stopped")
