# ZWEITOOLS


## ZapiClient 

Zweitip API client usage:

```python
#!/usr/bin/env python3
import logging
import sys
import json
from datetime import datetime as dt
from zweitools import ZapiClient
from zweitools import ZapiEndpoint
from zweitools import SearchDescriptor
from zweitools import SortOrder
from zweitools import DateOP


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Started")

    api_key = sys.argv[1]
    client = ZapiClient(api_key)

    search_descriptor = (
        SearchDescriptor()
        .limit(10)
        .offset(0)
        .sort("_id", SortOrder.DESC)
        .filtering_params(whole_word=False, ignore_case=True)
        .add_filter("tags", "banker")
        .add_filter("tags", "joker")
        .shape(["_id", "created_at"])
        #.local_time_created_at(dt(2022, 8, 26, 14, 45, 50), DateOP.GTE)
    )
    status, resp = client.get_many(ZapiEndpoint.MISC_DATA, search_descriptor)
    print(json.dumps(resp))

    logging.info("Finished")
```