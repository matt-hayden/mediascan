
import mediascan.cli

scan = mediascan.cli.scan

import sys
scan(*sys.argv[1:])

