from django.shortcuts import render
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.contrib.admin.views.decorators import staff_member_required

from core.models import *

from django.contrib.auth.models import User


@staff_member_required
@cache_page(60 * 5)
def events_members(request):
    context = {}
    persons_online = Person.objects.filter(participation='O').count()
    events = Event.objects.all()
    context["events"] = events
    context["persons_online"] = persons_online
    return render(request, 'members.html', context)

@staff_member_required
def all_persons(request):
    context = {}
    persons = Person.objects.all()
    context["persons"] = persons
    eur = EventUserRegistration.objects.all()
    return render(request, 'all.html', context)

@staff_member_required
def get_all_speakers(request):
    registrations = EventUserRegistration.objects.all().exclude(type__title="Участник")
    return render(request, "speakers.html", {"eurs": registrations})

@staff_member_required
def fulltimers(request):
    cheaters = [
        "58d7d39d-450f-41e6-acb9-a8d9903740a9",
        "0b8ed3c7-944b-42ea-8a6f-9a1c7ebffc46",
        "4b73a9f0-ef52-4fe1-a91c-e935ff54f9e5",
        "c823fc1e-675a-4558-becf-70e2370e7545",
        "b4adced4-dc12-4778-a8fb-c515dfcb073b",
        "f1180876-89ff-45bb-ba68-0f84754af2c5",
        "fcd894f6-a93f-4516-93af-704b133c5c22",
        "5533b958-65fb-4a3d-a73f-5c7352fbb960",
        "f9911383-bdb6-4dd3-afd3-1164afa6fd3c",
        "a630b2d9-3c3a-47f1-a5f6-5c63a0465874",
        "c3db6a92-f31b-4e61-8de3-c0e7925745d9",
        "8ad885a4-557c-47e2-92c8-e7e6faeeb26d",
        "cb167368-e64c-46fb-8c13-da477e898c57",
        "b427c66f-1dd9-4ff6-8f67-12480de8af0d",
        "860baf2a-8779-4346-8209-199dc11441ed",
        "cab29dc2-ae6d-4af2-a2f1-54355594d203",
        "cd5ad396-b2fd-42c4-a444-59dd0aaf4bd8",
        "05d0522a-12ca-495d-b921-dcbc7eef5123",
        "55277601-dd70-43c7-ac7c-87cea767b21f",
        "7efbf6df-8dfb-4605-8cd7-bcfad36e6f82",
        "0ab54c07-0a79-4811-b17c-f12de247aa57",
        "b3d11cbf-0387-419c-b52e-8907776dc5c2",
        "276c77d3-098f-41d7-97b7-2d653e7a3b15",
        "6d4feaab-70ab-482a-8639-f2bbfa0bee29",
        "43d11db4-a829-417b-8a70-c494af69a10b",
        "4412eb8b-d2f1-41e2-9c01-1cdc2d0736fb",
        "03d9bd98-dbee-4fd3-ae77-3c85639002d1",
        "593fc554-7469-4a8e-b69f-7ef21e2b8028",
        "782036ba-0624-4fd7-9772-db1e3428fcee",
        "5a709aac-07c0-41fd-8be7-6e8c1336442a",
        "aee2bc2f-b050-461a-9cdc-03097ada72ff",
        "d1253437-96d8-4483-be32-8fb5950b9ac6",
        "1582222c-9219-4f02-94a1-d0f573243e22",
        "660d4da1-7ffc-4ac5-a6a8-63e6a6c0bfd3",
        "c00ae2f6-b2ab-4c68-8a18-2205b62eec09",
        "a40992a6-5103-479f-8281-d8e67a241909",
        "5976e493-f770-493d-b87a-f3d6ae4a0276",
        "10a4bfc8-6bfa-45eb-b941-fdce63c27cbd",
        "100d1cfa-a70d-4e9d-a5b5-103b08b67364",
        "91e2ebd8-167c-473d-b23b-284cddda288b",
        "7f47709d-6874-4f95-92f5-f2851cd520a9",
        "27a2249d-8690-4ea4-961d-b4748d64dc6e",
        "0c2a422b-2303-427b-af11-2ae039ed23ba",
        "63d0c854-29b7-424a-90ac-cdea05f01f83",
        "6f82e1d9-ad80-409e-9cb6-d0cf28781c3a",
        "c473c58c-40e5-4161-ba32-f96defcc95cb",
        "b0682835-3fbd-4eba-9d9e-97441e24bb82",
        "50c7bb59-4110-4a98-a6a3-ae3f1c218518",
        "9c915205-e8a6-4ea1-9913-9f7d76bd2fcc",
        "a20a8a6d-01e0-499e-be4d-09c3ee8c1517",
        "5b2b7b21-4917-4aeb-a58e-bbbc0c732fe1",
        "82e40eea-16d1-4e74-b257-651f2aec941f",
        "7b522372-629c-4356-a3d6-6711808a77f4",
        "21bf8e88-ed1c-4bfb-b218-8520ba359223",
        "adb06129-e38e-45bb-ad27-57857f9d23c9",
        "b3722ef3-c708-45ce-a64a-459ed12e9842",
        "5708a117-3c1e-4f3d-9d93-dfeba5184d51",
        "79231625-61ac-4f66-a4ed-6edbb8767028",
        "1a83f52d-d1b0-4112-a470-f82612f0227f",
        "abea80db-c463-4e70-89be-ef42705aafc8",
        "3f283927-e6d2-41bd-8ebf-5e0d538bee70",
        "96436cc0-46bb-4b91-9a43-ad67fcdf6cb8",
        "fbfa99c2-4e43-43cf-babb-cff4123eb475",
        "74aacb1b-60a2-461a-aa02-03f7dc7641a0",
        "52dd1704-73b5-4da1-8fcb-4ac48711b196",
        "ec30e408-5ded-461b-b57e-026b0c11518d",
        "1c8e2747-6cc4-4210-9568-9ed0d80c19c1",
        "91192603-e589-4baa-b8c1-7bd810cfcc26",
        "5fabceff-481d-486d-80db-0d1fe5a70db0",
        "50f90cf4-d7e5-4674-83ff-a7dbbaa2a25f",
        "8d13d221-64a6-4755-b97f-416cdccb81d0",
        "a859aa3b-6bae-49b5-bb2e-19acefc48d54",
        "3d8a1343-2061-45fc-b7f0-f73544ae5071",
        "b6968363-4f7e-4549-998f-902ff5e0d146",
        "1fda8f5a-146c-451c-aaae-6ac412f3c5f4",
        "cc4a42ea-0967-4a1e-a7ed-de21b7303fa6",
        "9dc1c8c2-934e-43b1-87a1-b3af5b22f540",
        "0bc67c7a-8247-4954-905f-cb6335c1b69d",
        "2c4ff10b-3776-4a34-bf8c-d2d454bb5190",
        "29384451-53ea-4488-a06a-13518060524a",
        "fc1014f2-7b0f-43af-b45c-c0e76c19bf9d",
        "49209103-4f3d-4217-bde3-b6b303288c17",
        "fd05afe0-d2de-46f0-8b25-1a1d77065088",
        "3a37fc92-b5f8-4a07-8593-d3bb3614f79c",
        "aba7b644-5891-4e51-9f7c-d27c10c82c8f",
        "1a07a5df-415b-4dfc-96f5-da3abe4c6189",
        "9c4aa5a5-2524-4905-9791-a919a9876dd8",
        "d3d6a6c4-bfd5-410c-9a55-f01c135e06cf",
        "3395317d-d41d-4eda-baec-185ca96cf92c",
        "c5be0e3f-3733-4fbb-8e07-52cada321670",
        "7b62bcbd-df61-4c91-a85e-288712149a87",
        "4d76a943-7935-466f-ac26-720c14ca7809",
        "22dcb0a5-5349-41c8-a59e-aac6de278569",
        "8093126f-be2e-4546-b714-5e501ec826b2",
        "f318f6ce-ce7b-4ec0-bfc7-1800d0020a32",
        "d7bfc1f0-873d-4c93-80c8-2f5e6d8c2658",
        "1e5f89b7-f53c-4fb1-869f-f683f3c9529b",
        "11dac7c4-6651-4673-aeb0-01ac54066c60",
        "ff0bb193-7a0d-4da5-9c11-3155935d6ac9",
        "8cf0e86d-8c99-4aef-9347-31feee155559",
        "02602d5c-7b30-485e-835e-98a38375ae7c",
        "b3fccb81-597f-458a-8ee5-78c9822afbed",
        "06f831aa-84ea-416a-b07b-848152cd4c2a",
        "9aef1d57-6abf-4680-97ac-b60f118a50ba",
        "2e089881-00f8-459f-9a31-5179da7fcc3f",
        "4917833d-cebb-48d3-aaff-ffac00cd4d25",
        "7ca2ec25-aa90-49cc-8b05-258fd9fe0d8f",
        "7b939fa0-0f26-44d7-b75f-1d2688b7f4eb",
        "8c464daa-9d81-4777-a2b6-7212b5f6bee7",
        "d3e93c25-1e0e-4338-ac62-7601c40ff80d",
        "047c78c0-4caf-4102-9fa2-5743699121a6",
        "d6f63080-1684-4858-8ca2-f295d1ff7ff2",
        "609d1408-ff5f-4c1c-b9e5-55920123c0d1",
        "d01a99ac-d9eb-4323-aafe-ee41668b75c8",
        "a2b9b852-2095-4b30-ad43-f266de80a501",
        "232fdecc-f3e6-4c64-9300-67705d517153",
        "c30dd54c-8001-40f9-ae0b-caf427694558",
        "09ac2ac3-2b59-4601-bf2c-b3254cca9f4b",
        "5b51a562-555b-4ca7-94f1-653050514b01",
        "76e88d58-ee92-4de7-9150-52cd0f0fb73b",
        "0f5d3e64-2ccf-46f1-b048-6121663d25ca",
        "a21cf444-e125-4ca8-b943-458e6e54b79d",
        "8b99b44f-ae40-4fb1-b01e-60e3ce127e05",
        "7e48d5e8-4555-473a-915a-dfef02b44033",
        "6b1a8e8a-aee8-46b1-bb2c-d1a215207384",
        "18c763f1-39cd-4ea5-9098-4e705c078281",
        "b747af6d-6745-4cb7-9dad-644861653439",
        "25f50c72-4535-4658-a14e-3a8e396f549c",
        "cf00cd98-1f1d-4058-821f-e545c400e842",
        "c9dfb5a3-a9bf-4a99-9db3-68d7cdf1aafa",
        "d2e13c13-3979-47a8-936a-6c14f74f0e41",
        "8dbf273e-a473-46a9-8341-75bb3582b5cb",
        "2e166419-4e76-4b8a-817b-687b1aca810f",
        "42c8ce72-d192-4458-aff7-550e038d1417",
        "575eb884-0bde-445c-aff4-66a38f27ee46",
        "adc227be-1353-41cd-a9df-e57e6c182281",
        "f64f659e-e090-461a-bc6b-922100f0e6b3",
        "d97314bc-f12f-44fb-bcff-92189cfb88d8",
        "18f0865a-435d-4078-a1f1-2f89dfb6345e",
        "df22d4c6-4bce-4ef8-b25d-a2fcc81f31ee",
        "c3933ae5-e465-45a6-ba74-db38e6048248",
        "b2d919e8-692b-47f9-8824-693569c68b74",
        "0a79afec-7106-4006-9b38-6e5e13d90e7b",
        "fcab94d9-4197-4e25-82ea-016a1c77f169",
        "6d81a2d5-56de-4fe5-8005-d328f49383ae",
        "e94f56fc-7843-41f5-9e65-ce00227b2fe5",
        "46c59e15-6821-4920-9172-137a7424d939",
        "c9430e25-946a-4244-b6bd-7bbcae09e36e",
        "c8dc3827-c301-46ae-b005-8e4cd82094e3",
        "c1c02a06-c7f7-4117-8f7b-574556c7b740",
    ]
    persons = Person.objects.filter(Q(participation='O') & ~Q(id__in=cheaters))
    return render(request, "fulltimers.html", {"persons": persons})
