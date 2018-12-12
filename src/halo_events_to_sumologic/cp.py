import cloudpassage


class CPClient:
    def __init__(self, api_key, api_secret):
        self.session = cloudpassage.HaloSession(api_key, api_secret)
        self.server = cloudpassage.Server(session)
        self.server_group = cloudpassage.ServerGroup(session)
        self.scanner = cloudpassage.Scan(session)
        self.httphelper = cloudpassage.HttpHelper(session)

  def list_groups(self):
    groups = self.server_group.list_all()
    return groups

  def list_servers(self):
    servers = self.server.list_all()
    return servers

  def find_object_in_dict_list(self, dict_list, search_key, search_value):
    obj = next((o for o in dict_list if o[search_key].lower() == search_value.lower()), None)
    return obj

  def find_server_group_by_key(self, search_key, search_value):
    groups = self.list_groups()
    group  = self.find_object_in_dict_list(groups, search_key, search_value)

    if group == None:
      raise Exception("No server group found matching the \"" + search_key + "\", with \"" + search_value + "\"")

    return group

  def find_server_by_key(self, search_key, search_value):
    servers = self.list_servers()
    server  = self.find_object_in_dict_list(servers, search_key, search_value)

    if server == None:
      raise Exception("No server found matching the \"" + search_key + "\", with \"" + search_value + "\"")

    return server

  def list_servers_in_group(self, group_name):
    group = self.find_server_group_by_key("name", group_name)
    return self.server_group.list_members(group['id'])

  # server_ref can be a server_label or object
  def scan_server(self, server_ref, scan_type):
    if type(server_ref).__name__ == "str":
      server_id = self.find_server_by_key("server_label", server_ref)['id']
    else:
      server_id = server_ref['id']

    return self.scanner.initiate_scan(server_id, scan_type)

  def scan_servers_in_group(self, group_name, scan_type):
    servers = self.list_servers_in_group(group_name)

    if len(servers) == 0:
      raise Exception("No servers found in the server group named: \"" + group_name + "\"")

    for s in servers:
      self.scan_server(s, scan_type)

    return

  def active_issues(self):
    #issues              = self.httphelper.get("/v2/issues?status=active")["count"]
    #critical_issues     = self.httphelper.get("/v2/issues?status=active&critical=True")["count"]
    critical_issues = self.httphelper.get("/v1/issues?status=active&critical=True")["count"]
    non_critical_issues = self.httphelper.get("/v2/issues?status=active&critical=False")["count"]

    #return issues, critical_issues, non_critical_issues
    return critical_issues, non_critical_issues

  def assign_server_to_group(self, server_name, group_name):
    server = self.find_server_by_key("server_label", server_name)
    group  = self.find_server_group_by_key("name", group_name)

    if server['group_name'] == group['name']:
      raise Exception("Error. The server named: \"" + server_name + "\", is already in the group named: \"" + group_name + "\"")

    response = self.server.assign_group(server['id'], group['id'])

    if response == True:
      return "Successfully assigned the server named: \"" + server_name + "\", to the \"" + group_name + "\" server group"
    else:
      return "Failed to assign the server named: \"" + server_name + "\", to the \"" + group_name + "\" server group"
