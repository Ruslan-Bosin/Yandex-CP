### Create database tables:

```shell
export FLASK_APP=app
flask shell 
```
```python
from app.models import db
from app.models import ClientModel, OrganizationModel, RecordModel, AdminModel
db.create_all()
```