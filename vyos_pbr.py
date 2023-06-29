import requests
import urllib3

vyos_list = {
    'MPLS': '100.64.217.129:8080'
}
tloc_list = {
    'MPLS': {
        'MEX1': '172.30.217.192/30',
        'MEX2': '172.30.217.196/30',
        'PHL': '172.30.217.200/30',
        'BOS': '172.30.217.204/30',
        'LAS': '172.30.217.208/30',
        'DFW': '172.30.217.212/30',
        'MIA2': '172.30.217.216/30',
        'All Sites': '172.30.217.0/24'
    }
}

urllib3.disable_warnings()


def list_routes(vyos, tlocs):
    payload = {'data': '{"op": "showConfig", "path": ["policy", "route", "PBR"]}',
               'key': 'my-python-key'}
    url = f"https://{vyos}/retrieve"
    response = requests.request("POST", url, headers={}, data=payload, verify=False)
    try:
        if response.json()['data']['rule']:
            rules = response.json()['data']['rule']
            for rule in rules:
                print(f"  {rule}: {list(tlocs.keys())[list(tlocs.values()).index(rules[rule]['source']['address'])]} --> "
                      f"{list(tlocs.keys())[list(tlocs.values()).index(rules[rule]['destination']['address'])]}")
    except (KeyError, TypeError):
        print('  No Current Redirects')
        rules = None

    return rules


def delete_route(vyos, route_num):
    payload = {'data': f'{{"op": "delete", "path": ["policy", "route", "PBR", "rule", "{route_num}"]}}',
               'key': 'my-python-key'}
    url = f"https://{vyos}/configure"
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    print(f'Result: {response.json()}')


def add_route(vyos, route_num, source, destination):

    op_path = f'"op": "set", "path":["policy", "route", "PBR", "rule", "{route_num}", '
    payload = {
        "data": '['
                f'{{{op_path}"source", "address", "{source}"]}},'
                f'{{{op_path}"destination", "address", "{destination}"]}},'
                f'{{{op_path}"set", "table", "1"]}}'
                ']',
        "key": "my-python-key"
    }
    url = f"https://{vyos}/configure"
    response = requests.request("POST", url, headers={}, data=payload, verify=False)

    print(f'Result: {response.json()}')


if __name__ == '__main__':

    carrier = 0
    while carrier != '2':
        for provider in vyos_list:
            print(f'\n\nCurrent {provider} Tunnels Redirected:')
            list_routes(vyos_list[provider], tloc_list[provider])
        print('\n\nService Providers:')
        for num, provider in enumerate(vyos_list):
            print(f'  {num}: {provider}')
        print(f'  {num + 1}: Exit Tool')
        vyos_choice = input('\nWhich provider do you want to edit? ')
        if int(vyos_choice) == num + 1:
            break
        vyos_address = list(vyos_list.values())[int(vyos_choice)]
        provider_tlocs = list(tloc_list.values())[int(vyos_choice)]

        choice = 0
        while choice != '4':
            print(f'\n\nCurrent {list(vyos_list.keys())[int(vyos_choice)]} Tunnels Redirected:')
            routes = list_routes(vyos_address, provider_tlocs)
            print('\nChoose an action:\n'
                  '  1) Add a Redirect\n'
                  '  2) Delete a Redirect\n'
                  '  3) Clear All Redirects\n'
                  '  4) Exit to Provider Menu\n')
            choice = input('Enter choice: ')

            if choice == '1':
                if routes is None:
                    route_number = 1
                else:
                    route_number = int(list(routes.keys())[len(routes) - 1]) + 1
                print('\nSite List:')
                for num, site in enumerate(provider_tlocs):
                    print(f'  {num}: {site}')
                source_site = input("\nEnter source site:")
                destination_site = input("Enter destination site:")
                add_route(vyos_address, route_number,
                          list(provider_tlocs.values())[int(source_site)],
                          list(provider_tlocs.values())[int(destination_site)])

            elif choice == '2':
                route_choice = input('Which route number: ')
                delete_route(vyos_address, route_choice)

            elif choice == '3':
                for route in routes:
                    print(f'Deleting Rule {route}')
                    delete_route(vyos_address, route)
