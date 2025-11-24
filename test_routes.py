import main
routes = [r.path for r in main.app.routes]
voice_sub_routes = [p for p in routes if 'voice' in p or 'subscription' in p]
print('Voice/subscription routes:', voice_sub_routes)
print('All routes:', routes)
