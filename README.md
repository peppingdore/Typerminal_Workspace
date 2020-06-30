### Collection of files that get loaded in my Typerminal


**b_main.py** should be treated as if it was named user_main.py.
## My user_main.py
```python
# The reason i'm having this file to just link to some folder, is that I have to work with 2 instances of Typerminal(Debug and Shipment builds).
#  And I want their workspaces to be the same.

import sys

sys.path.append("E:/typerminal_workspace")

from b_main import *
```
