import csv
from flask import send_file
from flask import Flask, render_template, request
import ipaddress

app = Flask(__name__)

vlan_plans = []

def get_wildcard_mask(netmask):
    return ".".join(
        str(255 - int(octet))
        for octet in str(netmask).split(".")
    )

@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    error = None

    if request.method == "POST":

        vlan_id = request.form["vlan_id"]
        department = request.form["department"]
        network_input = request.form["network"]

        try:

            network = ipaddress.ip_network(network_input)

            result = {
                "vlan_id": vlan_id,
                "department": department,
                "network_address": network.network_address,
                "broadcast_address": network.broadcast_address,
                "subnet_mask": network.netmask,
                "wildcard_mask": get_wildcard_mask(network.netmask),
                "total_hosts": network.num_addresses - 2,
                "first_host": list(network.hosts())[0],
                "last_host": list(network.hosts())[-1]
            }

            vlan_plans.append(result)

        except ValueError:
            error = "Invalid network address. Please enter a valid CIDR notation."

    return render_template(
        "index.html",
        result=result,
        error=error,
        vlan_plans=vlan_plans
    )

@app.route("/export")
def export_csv():

    filename = "vlan_plans.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "VLAN ID",
            "Department",
            "Network",
            "Hosts"
        ])

        for vlan in vlan_plans:

            writer.writerow([
                vlan["vlan_id"],
                vlan["department"],
                vlan["network_address"],
                vlan["total_hosts"]
            ])

    return send_file(
        filename,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)