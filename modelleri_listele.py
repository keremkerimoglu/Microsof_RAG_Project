import foundry_local_sdk as foundry_local

config = foundry_local.Configuration(app_name="local_Asistan")
manager = foundry_local.FoundryLocalManager(config)

print("Katalogdaki Tüm Modeller:")
for m in manager.catalog.list_models():
    isim = getattr(m, 'name', '') or getattr(m, 'id', '')
    print(f"- {isim}")