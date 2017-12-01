from django.contrib import admin
from .models import WorkSpace, LeaveMessageAsk, LeaveMessageResponse

# Register your models here.
admin.site.register(WorkSpace)
admin.site.register(LeaveMessageAsk)
admin.site.register(LeaveMessageResponse)
