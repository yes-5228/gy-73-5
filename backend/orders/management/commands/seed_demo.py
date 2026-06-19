from datetime import date, time, timedelta

from django.core.management.base import BaseCommand

from orders.models import MoveOrder
from tracking.models import ProgressEvent
from workers.models import Worker


class Command(BaseCommand):
    help = "Seed demo workers and moving orders."

    def handle(self, *args, **options):
        workers = [
            {
                "name": "张师傅",
                "phone": "13800000001",
                "vehicle": "4.2米厢货",
                "service_area": "浦东新区",
                "rating": 4.9,
            },
            {
                "name": "李师傅",
                "phone": "13800000002",
                "vehicle": "金杯面包车",
                "service_area": "徐汇区",
                "rating": 4.8,
            },
            {
                "name": "王师傅",
                "phone": "13800000003",
                "vehicle": "6.8米货车",
                "service_area": "静安区",
                "rating": 4.7,
            },
        ]
        worker_objects = []
        for data in workers:
            worker, _ = Worker.objects.get_or_create(phone=data["phone"], defaults=data)
            worker_objects.append(worker)

        if MoveOrder.objects.exists():
            self.stdout.write(self.style.SUCCESS("Demo data already exists."))
            return

        order1 = MoveOrder.objects.create(
            customer_name="陈女士",
            customer_phone="13900000088",
            origin="上海市徐汇区漕溪北路 88 号",
            destination="上海市浦东新区张江路 168 号",
            move_date=date.today() + timedelta(days=2),
            move_time=time(9, 30),
            items="两室一厅家具、冰箱、洗衣机、纸箱 20 个",
            note="需要拆装一张双人床",
        )
        ProgressEvent.objects.create(order=order1, stage=ProgressEvent.STAGE_CREATED, message="客户已提交搬家预约")

        order2 = MoveOrder.objects.create(
            customer_name="刘先生",
            customer_phone="13900000089",
            origin="上海市浦东新区世纪大道 100 号",
            destination="上海市闵行区虹梅路 200 号",
            move_date=date.today() - timedelta(days=3),
            move_time=time(14, 0),
            items="一室一厅家具、纸箱 12 个",
            note="",
            status=MoveOrder.STATUS_COMPLETED,
            settlement_status=MoveOrder.SETTLEMENT_CONFIRMED,
            assigned_to=worker_objects[0],
            claimed_by=worker_objects[0],
        )
        ProgressEvent.objects.create(order=order2, stage=ProgressEvent.STAGE_CREATED, message="客户已提交搬家预约")
        ProgressEvent.objects.create(order=order2, stage=ProgressEvent.STAGE_COMPLETED, worker=worker_objects[0], message="搬家服务已完成")

        order3 = MoveOrder.objects.create(
            customer_name="赵女士",
            customer_phone="13900000090",
            origin="上海市杨浦区五角场 50 号",
            destination="上海市宝山区共富路 80 号",
            move_date=date.today() - timedelta(days=5),
            move_time=time(10, 0),
            items="三室一厅家具、钢琴、家电若干",
            note="钢琴需要特别注意",
            status=MoveOrder.STATUS_COMPLETED,
            settlement_status=MoveOrder.SETTLEMENT_PENDING,
            assigned_to=worker_objects[1],
            claimed_by=worker_objects[1],
        )
        ProgressEvent.objects.create(order=order3, stage=ProgressEvent.STAGE_CREATED, message="客户已提交搬家预约")
        ProgressEvent.objects.create(order=order3, stage=ProgressEvent.STAGE_COMPLETED, worker=worker_objects[1], message="搬家服务已完成")

        order4 = MoveOrder.objects.create(
            customer_name="孙先生",
            customer_phone="13900000091",
            origin="上海市长宁区仙霞路 120 号",
            destination="上海市普陀区长寿路 200 号",
            move_date=date.today() - timedelta(days=7),
            move_time=time(8, 30),
            items="两室一厅家具",
            note="",
            status=MoveOrder.STATUS_COMPLETED,
            exception_status=MoveOrder.EXCEPTION_OPEN,
            settlement_status=MoveOrder.SETTLEMENT_CONFIRMED,
            assigned_to=worker_objects[2],
            claimed_by=worker_objects[2],
        )
        ProgressEvent.objects.create(order=order4, stage=ProgressEvent.STAGE_CREATED, message="客户已提交搬家预约")
        ProgressEvent.objects.create(order=order4, stage=ProgressEvent.STAGE_COMPLETED, worker=worker_objects[2], message="搬家服务已完成")

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
