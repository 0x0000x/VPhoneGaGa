import xml.etree.ElementTree as ET

# Define the namespace
ANDROID_NS = "http://schemas.android.com/apk/res/android"

# Register the namespace
ET.register_namespace('android', ANDROID_NS)

# Define the activity and service templates with namespace prefixes
activity_template = """\
<activity xmlns:android="http://schemas.android.com/apk/res/android"
    android:autoRemoveFromRecents="true"
    android:configChanges="keyboardHidden|orientation|screenLayout|screenSize"
    android:exported="true"
    android:label="光速虚拟机({number})"
    android:launchMode="singleInstance"
    android:maxAspectRatio="2.4"
    android:name="com.vphonegaga.titan.MyNativeActivity{number}"
    android:process=":instance{number}"
    android:taskAffinity="com.vphonegaga.titan.instance{number}"
    android:theme="@style/FullscreenTheme">
    <meta-data android:name="android.app.lib_name" android:value="VPhoneGaGaLib"/>
    <intent-filter>
        <action android:name="com.vphonegaga.titan.MyNativeActivity{number}"/>
        <category android:name="android.intent.category.CATEGORY_LAUNCHER"/>
    </intent-filter>
</activity>
"""

service_template = """\
<service xmlns:android="http://schemas.android.com/apk/res/android"
    android:enabled="true"
    android:exported="false"
    android:name="com.vphonegaga.titan.VPhoneInstance{number}"
    android:process=":instance{number}">
    <intent-filter>
        <action android:name="com.vphonegaga.titan.IVPhoneInstance"/>
    </intent-filter>
</service>
"""

# Load the AndroidManifest.xml file
manifest_file = "AndroidManifest.xml"
tree = ET.parse(manifest_file)
root = tree.getroot()

# Find the application node to append the activities and services
application_node = root.find("application")

if application_node is None:
    raise ValueError("No <application> tag found in the AndroidManifest.xml")

# Function to find an element by attribute
def find_element_by_attribute(tag, attribute_name, attribute_value):
    for elem in application_node.findall(tag):
        if elem.get(f"{{{ANDROID_NS}}}{attribute_name}") == attribute_value:
            return elem
    return None

# Find the existing activity and service elements to append the new entries under
existing_activity = find_element_by_attribute("activity", "name", "com.vphonegaga.titan.MyNativeActivity48")
existing_service = find_element_by_attribute("service", "name", "com.vphonegaga.titan.VPhoneInstance48")

# Debugging information
if existing_activity is None:
    raise ValueError("The specified activity element was not found in the AndroidManifest.xml")

if existing_service is None:
    raise ValueError("The specified service element was not found in the AndroidManifest.xml")

# Function to insert element after a specific element
def insert_after(parent, target, new_element):
    found = False
    for i, elem in enumerate(parent):
        if elem == target:
            parent.insert(i + 1, new_element)
            found = True
            break
    if not found:
        parent.append(new_element)

# Generate and append the activity and service entries
for i in range(49,480):
    number = str(i)

    # Generate activity entry
    activity_entry = activity_template.format(number=number)
    activity_element = ET.fromstring(activity_entry)
    insert_after(application_node, existing_activity, activity_element)  # Append after the existing activity element
    existing_activity = activity_element  # Update existing_activity to the newly inserted element

    # Generate service entry
    service_entry = service_template.format(number=number)
    service_element = ET.fromstring(service_entry)
    insert_after(application_node, existing_service, service_element)  # Append after the existing service element
    existing_service = service_element  # Update existing_service to the newly inserted element

# Write the modified manifest back to the file
tree.write(manifest_file, encoding="utf-8", xml_declaration=True)

print("AndroidManifest.xml has been updated.")
