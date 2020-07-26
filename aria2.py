import aria2p
import time

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

for one_dl in aria2.get_downloads():
    gid = one_dl.gid
    if (one_dl.is_complete):
        aria2.remove([one_dl])
    elif (one_dl.has_failed):
        if (aria2.resume([one_dl])):
            time.sleep(1)
            if (one_dl.has_failed):
                self.failure_name.append(one_dl.name)
                aria2.remove([one_dl])
