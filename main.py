class Phone:
    def __init__(self, number, name):
        self.number = number  # Phone number (string)
        self.name = name      # Phone owner's name (string)
        self.state = 'onhook'  # Phone state: 'onhook', 'offhook', 'ringing', 'dialing', 'calling', 'connected'
        self.current_call = None  # Holds the current call participants
        self.ringing_from = None  # Who is calling this phone
        self.call_type = 'normal'

    def __str__(self):
        # Return a string representation of the phone's status
        status = f"{self.name} ({self.number}): {self.state}"
        if self.current_call:
            if isinstance(self.current_call, list):
                # In a conference call
                others = ', '.join(p.name for p in self.current_call if p != self)
                status += f" (talking to {others})"
            else:
                # Talking to one other phone
                status += f" (talking to {self.current_call.name})"
        return status

class TelephoneSystem:
    def __init__(self):
        self.phones = {}  # Dictionary to store phones by their number

    def load_phones(self, filename):
        # Load phone numbers and names from a specified file
        with open(filename, 'r') as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        number, name = parts[0], ' '.join(parts[1:])
                        # Validate phone number and name
                        if len(number) == 5 and number.isdigit() and len(name) <= 12 and name.isalpha():
                            self.phones[number] = Phone(number, name)
                        else:
                            print(f"Ignored invalid entry: {line.strip()}")

    def find_phone(self, identifier):
        # Find a phone by number or name
        phone = self.phones.get(identifier)
        if phone:
            return phone
        for p in self.phones.values():
            if p.name == identifier:
                return p
        return None

    def status(self):
        # Display the status of each phone in the system
        for phone in self.phones.values():
            print(phone)

    def offhook(self, identifier):
        # Put a phone offhook
        phone = self.find_phone(identifier)
        if phone:
            if phone.state in ['offhook', 'dialing', 'calling', 'connected']:
                # Already offhook or in a call
                print(f"{phone.name} is already offhook.")
            else:
                phone.state = 'offhook'
                print(f"{phone.name} hears dialtone.")
        else:
            print(f"Phone {identifier} not found.")

    def onhook(self, identifier):
        # Put a phone onhook
        phone = self.find_phone(identifier)
        if phone:
            if phone.state == 'onhook':
                print(f"{phone.name} is already onhook.")
            else:
                # Disconnect from any calls
                if phone.current_call:
                    if isinstance(phone.current_call, list):
                        # Conference call
                        participants = phone.current_call
                        participants.remove(phone)
                        if len(participants) > 2:
                            # Update current_call for remaining participants
                            for p in participants:
                                p.current_call = participants
                        elif len(participants) == 2:
                            # Two participants left revert to normal call
                            remaining_phone1, remaining_phone2 = participants
                            remaining_phone1.current_call = remaining_phone2
                            remaining_phone2.current_call = remaining_phone1
                            remaining_phone1.state = 'connected'
                            remaining_phone2.state = 'connected'
                            print(f"{remaining_phone1.name} and {remaining_phone2.name} are talking.")
                        elif len(participants) == 1:
                            # Only one participant left
                            remaining_phone = participants[0]
                            remaining_phone.current_call = None
                            remaining_phone.state = 'offhook'
                        phone.current_call = None # Clear current_call
                        print(f"{phone.name} hangs up from conference.")
                    else:
                        # Normal call
                        other = phone.current_call
                        other.current_call = None
                        if other.state != 'onhook':
                            other.state = 'offhook'
                            print(f"{other.name} hears silence.")
                        phone.current_call = None
                    phone.state = 'onhook'
                elif phone.state == 'ringing':
                    # Missed call
                    phone.state = 'onhook'
                    caller = phone.ringing_from
                    if caller and caller.state == 'calling': # Check if caller is still calling 
                        if caller.call_type == 'normal': 
                            # Missed normal call
                            print(f"{caller.name} hears silence.")
                            caller.state = 'offhook'
                            caller.current_call = None
                        elif caller.call_type == 'transfer': 
                            # Failed transfer
                            caller.state = 'connected'
                            caller.current_call = caller.current_call
                            print(f"Transfer to {phone.name} failed.")
                            print(f"{caller.name} and {caller.current_call.name} are talking.")
                            phone.ringing_from.call_type = 'normal'
                            caller.current_call.call_type = 'normal'
                        elif caller.call_type == 'conference':
                            # Failed Conference
                            # Unpack participants
                            remaining_phone1, remaining_phone2 = caller.current_call[0], caller.current_call[1] 
                            # Reset states
                            remaining_phone1.state, remaining_phone2.state = 'connected', 'connected'
                            # Reset failed conference call to normal call
                            remaining_phone1.current_call, remaining_phone2.current_call = remaining_phone2, remaining_phone1
                            # Reset call types
                            remaining_phone1.call_type, remaining_phone2.call_type = 'normal', 'normal'
                            print(f"Conference call failed.")
                            print(f"{remaining_phone1.name} and {remaining_phone2.name} are talking.")
                    phone.ringing_from = None
                else:
                    phone.state = 'onhook'
                print(f"{phone.name} is now onhook.")
        else:
            print(f"Phone {identifier} not found.")

    def call(self, caller_id, receiver_id):
        # Initiate a call from one phone to another
        caller = self.find_phone(caller_id)
        receiver = self.find_phone(receiver_id)

        if not caller:
            print(f"Caller {caller_id} not found.")
            return
        if not receiver:
            print(f"{caller.name} hears denial.")
            return

        if caller.state != 'offhook':
            print(f"{caller.name} hears silence.")
            return

        if receiver.state == 'onhook':
            # Set up the call
            caller.state = 'calling'
            caller.current_call = receiver
            caller.call_type = 'normal'  # Reset call_type to 'normal' when initiating a normal call
            receiver.state = 'ringing'
            receiver.ringing_from = caller
            print(f"{caller.name} hears ringback.")
            print(f"{receiver.name} hears ringing.")
        elif receiver.state in ['offhook', 'dialing', 'calling', 'connected', 'ringing']:
            print(f"{caller.name} hears busy.")
        else:
            print(f"{caller.name} hears denial.")

    def answer_call(self, identifier):
        # Answer a ringing phone
        phone = self.find_phone(identifier)
        if phone:
            if phone.state == 'ringing':
                caller = phone.ringing_from
                if not caller:
                    print(f"Error: No caller information.")
                    return
                if caller.state == 'calling' and caller.current_call:
                    if caller.call_type == 'conference':
                        # Conference call
                        if isinstance(caller.current_call, list):
                            participants = caller.current_call
                        else:
                            participants = [caller, caller.current_call]
                        # Check if phone is already in participants
                        if phone not in participants:
                            participants.append(phone)
                        for p in participants:
                            p.current_call = participants
                            p.state = 'connected'
                        phone.state = 'connected'
                        print(f"{', '.join([p.name for p in participants])} are talking.")
                    elif caller.call_type == 'transfer':
                        # Transfer call
                        other_party = caller.current_call
                        # Connect other_party and phone
                        other_party.current_call = phone
                        other_party.state = 'connected'
                        phone.current_call = other_party
                        phone.state = 'connected'
                        # Disconnect caller
                        caller.current_call = None
                        caller.state = 'offhook'
                        print(f"{other_party.name} and {phone.name} are talking.")
                        print(f"{caller.name} hears silence.")
                    else:
                        # Normal call
                        phone.state = 'connected'
                        phone.current_call = caller
                        caller.state = 'connected'
                        caller.current_call = phone
                        print(f"{caller.name} and {phone.name} are talking.")
                    # Clear ringing_from and reset call_type
                    phone.ringing_from = None
                    caller.call_type = 'normal'
                else:
                    # Normal call
                    phone.state = 'connected'
                    phone.current_call = caller
                    caller.state = 'connected'
                    caller.current_call = phone
                    print(f"{caller.name} and {phone.name} are talking.")
                    phone.ringing_from = None
            else:
                print(f"{phone.name} is not ringing.")
        else:
            print(f"Phone {identifier} not found.")

    def transfer(self, identifier, new_receiver_id):
        # Transfer an ongoing call to a new phone
        caller = self.find_phone(identifier)
        new_receiver = self.find_phone(new_receiver_id)

        if not caller or not new_receiver:
            print(f"{identifier} hears denial.")
            return

        if caller.state != 'connected' or not caller.current_call:
            print(f"{caller.name} hears denial.")
            return

        other_party = caller.current_call
        if isinstance(other_party, list):
            # Cannot transfer a conference call
            print(f"{caller.name} hears denial.")
            return

        if new_receiver.state == 'onhook':
            # Begin transfer process
            caller.state = 'calling'
            caller.call_type = 'transfer'  # Set call type
            caller.current_call = other_party  # Keep track of the other party
            new_receiver.state = 'ringing'
            new_receiver.ringing_from = caller
            print(f"{caller.name} hears ringback.")
            print(f"{new_receiver.name} hears ringing.")
        else:
            print(f"{caller.name} hears denial.")

    def conference(self, identifier, third_party_id):
        # Add a third party to an ongoing call
        caller = self.find_phone(identifier)
        third_party = self.find_phone(third_party_id)

        if not caller or not third_party:
            print(f"{identifier} hears denial.")
            return

        if caller.state != 'connected' or not caller.current_call:
            print(f"{caller.name} hears denial.")
            return

        if third_party.state == 'onhook':
            other_party = caller.current_call
            if isinstance(other_party, list):
                participants = other_party
            else:
                participants = [caller, other_party]
            if len(participants) >= 3:
                print(f"{caller.name} hears denial.")
                return
            participants.append(third_party)
            caller.current_call = participants
            caller.state = 'calling'
            caller.call_type = 'conference'  # Set call type
            third_party.state = 'ringing'
            third_party.ringing_from = caller
            print(f"{caller.name} hears ringback.")
            print(f"{third_party.name} hears ringing.")
        else:
            print(f"{caller.name} hears denial.")

    def pickup(self, identifier):
        # Handle a phone going offhook
        phone = self.find_phone(identifier)
        if not phone:
            print(f"Phone {identifier} not found.")
            return

        if phone.state == 'onhook':
            self.offhook(identifier)
            phone.call_type = 'normal'  # Reset call_type to 'normal' when going offhook
        elif phone.state == 'ringing':
            self.answer_call(identifier)
        elif phone.state in ['offhook', 'dialing', 'calling', 'connected']:
            print(f"{phone.name} hears silence.")
        else:
            print(f"{phone.name} hears denial.")


def main():
    system = TelephoneSystem()
    system.load_phones('phones.txt')

    while True:
        command = input("Enter command: ").strip()
        if not command:
            continue
        command_parts = command.split()
        if command.lower() == "status":
            system.status()
        elif len(command_parts) == 2:
            phone_id, action = command_parts
            action = action.lower()
            if action == "offhook":
                system.pickup(phone_id)
            elif action == "onhook":
                system.onhook(phone_id)
            else:
                print("Invalid command.")
        elif len(command_parts) == 3:
            phone_id, action, target_id = command_parts
            action = action.lower()
            if action == "call":
                system.call(phone_id, target_id)
            elif action == "transfer":
                system.transfer(phone_id, target_id)
            elif action == "conference":
                system.conference(phone_id, target_id)
            else:
                print("Invalid command.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
