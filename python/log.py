import logging
import time
logging.basicConfig(level=logging.INFO,
                    # filename='state-{0}.log'.format(time.time()),
                    # filemode='w',
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )