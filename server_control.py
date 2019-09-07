import zmq, time, subprocess, sys, socket, minestat, logging.handlers, os, secrets
from interruptingcow import timeout

if not os.path.exists("logs"):
    os.mkdir("logs")
logger = logging.getLogger()
file_handler = logging.handlers.RotatingFileHandler("logs/server-control.log", maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s [line %(lineno)d]"))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def system_start():
    logger.info("Starting the server, please wait...")

    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.REQ)
    zmq_socket.setsockopt(zmq.LINGER, 0) # The default value is -1, which means wait until all messages have been sent before allowing termination. Set to 0 to discard unsent messages immediately, and any positive integer will be the number of milliseconds to keep trying to send before discard.

    subprocess.run(["/usr/bin/sudo", "/usr/sbin/etherwake", "-i", "eth0", secrets.MAC_ADDRESS])
    logger.info("Sent Wake on LAN packet. Waiting 10 seconds for the server to switch on...")
    time.sleep(10)

    try:
        with timeout(5, exception=RuntimeError):
            logger.info("Attempting to connect to the control server...")
            zmq_socket.connect("tcp://" + secrets.LOCAL_IP + ":5555")
            logger.info("Connected. Server successfully switched on.")
            pass
        return {"result": "done"}
    except RuntimeError:
        logger.info("No response...")
        logger.info("The server could not be switched on")
        return {"result": "failed"}

    zmq_socket.close()
    zmq_context.term()

def vanilla_start():
    logger.info("Starting the server, please wait...")

    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.REQ)
    zmq_socket.setsockopt(zmq.LINGER, 0) # The default value is -1, which means wait until all messages have been sent before allowing termination. Set to 0 to discard unsent messages immediately, and any positive integer will be the number of milliseconds to keep trying to send before discard.

    subprocess.run(["/usr/bin/sudo ", "/usr/sbin/etherwake", "-i", "eth0", secrets.MAC_ADDRESS])
    logger.info("Sent Wake on LAN packet. Waiting 10 seconds for the server to switch on...")
    time.sleep(10)

    try:
        with timeout(5, exception=RuntimeError):
            logger.info("Attempting to connect to the control server...")
            zmq_socket.connect("tcp://" + secrets.LOCAL_IP + ":5555")
            logger.info("Connected. Sending \"start\" command...")
            zmq_socket.send_string("start")
            pass
        with timeout(5, exception=RuntimeError):
            logger.info("Done. Waiting for response...")
            response = zmq_socket.recv_string()
            pass
        if response == "done":
            logger.info("The server has been switched on ✅")
            zmq_socket.close()
            zmq_context.term()
            return {"result": "done"}
        else:
            logger.info("Received response: " + response)
            logger.info("The server was switched on but the Minecraft Server was not switched on")
            zmq_socket.close()
            zmq_context.term()
            return {"result": "failed"}
    except RuntimeError:
        logger.info("No response...")
        logger.info("The server could not be switched on")
        zmq_socket.close()
        zmq_context.term()
        return {"result": "failed"}

    zmq_socket.close()
    zmq_context.term()

def system_stop():
    logger.info("Stopping the server, please wait...")

    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.REQ)
    zmq_socket.setsockopt(zmq.LINGER, 0) # The default value is -1, which means wait until all messages have been sent before allowing termination. Set to 0 to discard unsent messages immediately, and any positive integer will be the number of milliseconds to keep trying to send before discard.

    # use os.path thingy to add danny bot's install folder to these path checks:
    # if os.path.exists("disable_stop.txt"):
    #     await message.channel.send("Not turning the server off because tech189 has requested that it stays on")
    # else:
    #     if os.path.exists("last_start.txt"):
    #         os.remove("last_start.txt")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with timeout(2, exception=RuntimeError):
                logger.info("Pinging the server to check if it's online...")
                s.connect((secrets.LOCAL_IP, 5555))
                logger.info("Ping successful.")
                pass
            with timeout(5, exception=RuntimeError):
                    logger.info("Attempting to connect to the control server...")
                    zmq_socket.connect("tcp://" + secrets.LOCAL_IP + ":5555")
                    logger.info("Connected. Sending \"stop\" command...")
                    zmq_socket.send_string("stop")
                    pass
            logger.info("Done. Waiting for response...")
            response = zmq_socket.recv_string()
            if response == "done":
                logger.info("Received response. Waiting 20 seconds for server to shut down...")
                time.sleep(20)
                s_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    with timeout(1, exception=RuntimeError):
                        logger.info("Pinging the server to check if it's online...")
                        s_2.connect((secrets.LOCAL_IP, 5555))
                        logger.info("Ping successful. The server could not be shut down")
                        zmq_socket.close()
                        zmq_context.term()
                        return {"result": "failed"}
                except RuntimeError:
                    logger.info("No response within 1 second. Therefore server is off")
                    logger.info("The server has been shut down 😴")
                    zmq_socket.close()
                    zmq_context.term()
                    return {"result": "done"}
                s_2.close()
            else:
                logger.info("Received response: " + response)
                logger.info("The server could not be shut down")
                zmq_socket.close()
                zmq_context.term()
                return {"result": "failed"}
        except RuntimeError:
            logger.info("The server seems to be off already, you can turn it on with `!server start`")
            zmq_socket.close()
            zmq_context.term()
            return {"result": "done"}
        s.close()
    except RuntimeError:
        logger.info("The server could not be shut down")
        zmq_socket.close()
        zmq_context.term()
        return {"result": "failed"}

    zmq_socket.close()
    zmq_context.term()
    try:
        with timeout(5, exception=RuntimeError):
            logger.info("Attempting to connect to the control server...")
            zmq_socket.connect("tcp://" + secrets.LOCAL_IP + ":5555")
            logger.info("Connected. Sending \"stop\" command...")
            zmq_socket.send_string("stop")
            pass
        with timeout(5, exception=RuntimeError):
            logger.info("Done. Waiting for response...")
            response = zmq_socket.recv_string()
            pass
        if response == "done":
            logger.info("The server has been switched on ✅")
            zmq_socket.close()
            zmq_context.term()
            return {"result": "done"}
        else:
            logger.info("Received response: " + response)
            logger.info("The server was switched on but the Minecraft Server was not switched on")
            zmq_socket.close()
            zmq_context.term()
            return {"result": "failed"}
    except RuntimeError:
        logger.info("No response...")
        logger.info("The server could not be switched on")
        zmq_socket.close()
        zmq_context.term()
        return {"result": "failed"}



def status():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with timeout(1, exception=RuntimeError):
            logger.info("Pinging the server to check if it's online...")
            sock.connect((secrets.LOCAL_IP, 5555))
            logger.info("Ping successful. The server is on.")
            pass
        sock.close()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with timeout(1, exception=RuntimeError):
                logger.info("Pinging the server to check if it's online...")
                sock.connect((secrets.LOCAL_IP, 25565))
                logger.info("Ping successful. The server is on.")
                pass
            ms = minestat.MineStat('tech189.duckdns.org', 25565)
            ms1 = 'Online ✅\nVersion %s - %s out of %s players\nLatency: %sms\nPort: 25565' % (ms.version, ms.current_players, ms.max_players, ms.latency)
        except RuntimeError:
            ms1 = 'Offline'
        sock.close()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with timeout(1, exception=RuntimeError):
                logger.info("Pinging the server to check if it's online...")
                sock.connect((secrets.LOCAL_IP, 25566))
                logger.info("Ping successful. The server is on.")
                pass
            sock.close()
            ms = minestat.MineStat('tech189.duckdns.org', 25566)
            ms2 = 'Online ✅\nVersion %s - %s out of %s players\nLatency: %sms\nModpack: %s\nPort: 25566' % (ms.version, ms.current_players, ms.max_players, ms.latency, ms.motd.decode("utf-8"))
        except RuntimeError:
            ms2 = 'Offline'
        return {"result": "online  ✅", "ms1": ms1, "ms2": ms2}
    except RuntimeError:
        logger.info("No response within 1 second. Therefore server is off")
        return {"result": "offline", "ms1": 'Offline', "ms2": 'Offline'}
    sock.close()

if "--system_start" in sys.argv:
    logger.info("COMMAND: system_start")
    print(system_start())
elif "--system_stop" in sys.argv:
    logger.info("COMMAND: system_stop")
    print(system_stop())
elif "--status" in sys.argv:
    logger.info("COMMAND: status")
    print(status())