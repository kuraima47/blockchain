import logging

try:
    _log_orig = logging.Logger._log

    def _kargs_log(self, level, msg, args, exc_info=None, extra=None, **kargs):
        kwmsg = "".join(" %s=%s" % (k, str(v)) for k, v in kargs.items())
        _log_orig(self, level, str(msg) + kwmsg, args, exc_info, extra)

    logging.Logger._log = _kargs_log
    get_logger = logging.getLogger

    def configure(config_string):
        level_mappings = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        configs = config_string.split(",")
        for config in configs:
            name, level_str = config.split(":") if ":" in config else ("", config)
            name = None if name == "" else name
            level = level_mappings.get(level_str.lower(), logging.INFO)
            if name:
                logging.getLogger(name).setLevel(level)
            else:
                logging.getLogger().setLevel(level)

    def configure_logging(
        level=logging.INFO,
        log_format="%(asctime)s [%(levelname)s] - %(name)s: %(message)s",
    ):
        logging.basicConfig(level=level, format=log_format)

    def getLogger(name):
        return logging.getLogger(name)

    def basicConfig():
        logging.basicConfig()

except:
    import logging


if __name__ == "__main__":
    logging.basicConfig()
    log = get_logger("test")
    log.warn("miner.new_block", block_hash="abcdef123", nonce=2234231)
