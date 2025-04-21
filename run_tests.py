import unittest

from og_log import LOG,LEVEL

if __name__ == "__main__":
    LOG.start()
    LOG.level(LEVEL.error)
    unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover("unit_tests"))

