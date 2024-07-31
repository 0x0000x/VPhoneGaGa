import os

# Define the template contents for the two types of files
template_vphone = """\
.class public Lcom/vphonegaga/titan/VPhoneInstance{number};
.super Lcom/vphonegaga/titan/VPhoneInstance;

# direct methods
.method public constructor <init>()V
    .locals 1

    const/16 v0, {value}

    invoke-direct {{p0, v0}}, Lcom/vphonegaga/titan/VPhoneInstance;-><init>(I)V

    return-void
.end method
"""

template_native_activity = """\
.class public Lcom/vphonegaga/titan/MyNativeActivity{number};
.super Lcom/vphonegaga/titan/MyNativeActivity;

# direct methods
.method public constructor <init>()V
    .locals 1

    const/16 v0, {value}

    invoke-direct {{p0, v0}}, Lcom/vphonegaga/titan/MyNativeActivity;-><init>(I)V

    return-void
.end method
"""

# Create files from 49 to 100
for i in range(49, 481):
    number = str(i)
    value = hex(i).replace('0x', '0x')  # Compute the hex value directly from the file number

    # Create VPhoneInstance file
    vphone_filename = f"VPhoneInstance{number}.smali"
    if not os.path.exists(vphone_filename):
        vphone_content = template_vphone.format(number=number, value=value)
        with open(vphone_filename, "w") as file:
            file.write(vphone_content)
        print(f"Created {vphone_filename}")

    # Create MyNativeActivity file
    native_activity_filename = f"MyNativeActivity{number}.smali"
    if not os.path.exists(native_activity_filename):
        native_activity_content = template_native_activity.format(number=number, value=value)
        with open(native_activity_filename, "w") as file:
            file.write(native_activity_content)
        print(f"Created {native_activity_filename}")

print("Files creation process completed.")
