import asyncio, json, os, logging

from datetime import datetime

class StorageRunner:

    def __init__(self, loop, packet_queue, config):
        self.logger = logging.getLogger(__name__)
        self.loop = loop
        self.queue = packet_queue
        self.config = config

    async def run(self):
        self.file_counter = 0
        storage_path_prefix = self.config['database']['storage_path']
        interval = int(self.config['database']['interval'])
        storage_type = self.config['database']['type']
        while True:
            now = datetime.now()
            await asyncio.sleep(0.7)
            if now.second % interval == 0:
                file_name = "Mbox {}-{}.txt".format( \
                   now.strftime("%Y-%m-%d-%H-%M-%S"), \
                   self.file_counter
                   )
                q_list = list()
                if self.queue.empty() is not True:
                    self.file_counter += 1
                while self.queue.empty() is not True:
                    q = self.queue.get_nowait()
                    q['MBoxId'] = "0x{:x}".format(q['MBoxId'])
                    self.logger.debug(q)
                    q_list.append(q)
                    with open(os.path.join(storage_path_prefix, file_name), 'a+') as f:
                        if storage_type == 'json':
                            f.write(json.dumps(q_list))
                        elif storage_type == 'sql':
                            for stmt in q_list:
                                attr = "({}, {}, {}, {}, {})".format(*stmt.keys())
                                values = "('{:x}', '{}', '{}', '{}', '{}')".format(*stmt.values())
                                sql_stmt = "INSERT INTO {} VALUES {}\n".format(attr, values)
                                self.logger.debug(sql_stmt)
                                f.write(sql_stmt)
                        else:
                            pass
