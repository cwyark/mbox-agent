import asyncio, json, os, logging

from datetime import datetime
import netifaces

class StorageRunner:

    def __init__(self, loop, packet_queue, config):
        self.logger = logging.getLogger(__name__)
        self.loop = loop
        self.queue = packet_queue
        self.config = config

    async def run(self):
        self.file_counter = 0
        _seq_num = 0
        storage_path_prefix = self.config['database']['storage_path']
        if os.path.isdir(storage_path_prefix) is False:
            os.mkdir(storage_path_prefix)
        interval = int(self.config['database']['interval'])
        storage_type = self.config['database']['type']
        target_nic = self.config['internet']['macid']
        try:
            mac_addr = netifaces.ifaddresses(target_nic)[netifaces.AF_LINK][0].get('addr')
        except:
            mac_addr = "ff:ff:ff:ff:ff:ff"
        while True:
            now = datetime.now()
            await asyncio.sleep(0.7)
            if now.second % interval == 0:
                file_name = "Mbox {}-{}.txt".format( \
                   now.strftime("%Y-%m-%d-%H-%M-%S"), \
                   self.file_counter
                   )
                q_list = list()
                while self.queue.empty() is not True:
                    q = self.queue.get_nowait()
                    q['MACid'] = mac_addr 
                    q['SequentialNumber'] = _seq_num
                    self.logger.info(q)
                    _seq_num += 1
                    q_list.append(q)
                if len(q_list) != 0:
                    self.file_counter += 1
                    with open(os.path.join(storage_path_prefix, file_name), 'a+') as f:
                        if storage_type == 'json':
                            f.write(json.dumps(q_list))
                        elif storage_type == 'sql':
                            for stmt in q_list:
                                attr = "({}, {}, {}, {}, {})".format(*stmt.keys())
                                values = "('{:x}', '{}', '{}', '{}', '{}')".format(*stmt.values())
                                sql_stmt = "INSERT INTO {} VALUES {}\n".format(attr, values)
                                f.write(sql_stmt)
                        else:
                            self.logger.info("Unsupport Storage method");
