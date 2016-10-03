//
// Programmer:	Craig Stuart Sapp
// Date:	Mon Jun  8 14:54:42 PDT 2009
// Filename:	testout.c
// Syntax:	C; Apple OSX CoreMIDI
// $Smake:	gcc -o %b %f -framework CoreMIDI -framework CoreServices
//              note: CoreServices needed for GetMacOSSStatusErrorString().
//
// Description:	This program plays a single MIDI note (middle C) on all 
//              MIDI output ports which the program can find.
//
// Derived from "Audio and MIDI on Mac OS X" Preliminary Documentation, 
// May 2001 Apple Computer, Inc. found in PDF form on the developer.apple.com
// website, as well as using links at the bottom of the file.
//

#include <CoreMIDI/CoreMIDI.h>    /* interface to MIDI in Macintosh OS X */
#include <unistd.h>               /* for sleep() function                */
#define MESSAGESIZE 3             /* byte count for MIDI note messages   */
#include <iostream>

using namespace std;

void playPacketListOnAllDevices   (MIDIPortRef     midiout, 
                                   const MIDIPacketList* pktlist);

/////////////////////////////////////////////////////////////////////////

int main(int argc, char **argv) {

   // Prepare MIDI Interface Client/Port for writing MIDI data:
   MIDIClientRef midiclient  = NULL;
   MIDIPortRef   midiout     = NULL;
   OSStatus status;
   if (status = MIDIClientCreate(CFSTR("TeStInG"), NULL, NULL, &midiclient)) {
       printf("Error trying to create MIDI Client structure: %d\n", status);
//       printf("%s\n", GetMacOSStatusErrorString(status));
       exit(status);
   }
   if (status = MIDIOutputPortCreate(midiclient, CFSTR("mio"), &midiout)) {
       printf("Error trying to create MIDI output port: %d\n", status);
//       printf("%s\n", GetMacOSStatusErrorString(status));
       exit(status);
   }


   ItemCount nDests = MIDIGetNumberOfDestinations();
   ItemCount iDest;
   MIDIEndpointRef dest;
    MIDISysexSendRequest request[8];

    unsigned char data[4104];
    FILE *ptr;
    ptr = fopen(argv[1], "rb");
    int count = fread(data,1, 4104,ptr);
    cout << count << ": ";
    for (int i = 0; i < 10; ++i) {
        cout << (int)data[i] << ' ';
    }
    cout << " ... ";
    for (int i = 4096; i < 4104; ++i) {
        cout << (int)data[i] << ' ';
    }
    cout << endl;
   for(iDest=nDests-1; iDest<nDests; iDest++) {
       cout << iDest << endl;
      dest = MIDIGetDestination(iDest);
#if 0
      MIDIEntityRef ref;
      MIDIEndPointGetEntity(dest, &ref);
      MIDIDeviceRef device;
      MIDIEntityGetDevice(ref, &device);
      cout << "dest=" << dest << endl;
#endif
       request[iDest].destination = dest;
       request[iDest].data = data;
       request[iDest].bytesToSend = 4104;
       request[iDest].complete = 0;
       request[iDest].completionProc = NULL;
       request[iDest].completionRefCon = NULL;
       cout << "status=" << status << endl;
    if (status = MIDISendSysex(&request[iDest])) {
          printf("Problem sendint MIDI data on port %d\n", iDest);
//          printf("%s\n", GetMacOSStatusErrorString(status));
          exit(status);
      }
   }
   sleep(2);
   bool unfinished = false;
   while (unfinished) {
       unfinished = false;
       for(iDest=nDests-1; iDest<nDests; iDest++) {
           if (!request[iDest].complete) {
               unfinished = true;
           }
       }
   }

#if 0

   // Prepare a MIDI Note-On message to send 
   MIDITimeStamp timestamp = 0;   // 0 will mean play now. 
   Byte buffer[1024];             // storage space for MIDI Packets (max 65536)
   MIDIPacketList *packetlist = (MIDIPacketList*)buffer;
   MIDIPacket *currentpacket = MIDIPacketListInit(packetlist);
   Byte noteon[MESSAGESIZE] = {0x90, 60, 90};
   currentpacket = MIDIPacketListAdd(packetlist, sizeof(buffer), 
         currentpacket, timestamp, MESSAGESIZE, noteon);

   // send the MIDI data and wait for one second:
   playPacketListOnAllDevices(midiout, packetlist);
   sleep(1);

   // Prepare a MIDI Note-Off message to send
   currentpacket = MIDIPacketListInit(packetlist);
   Byte noteoff[MESSAGESIZE] = {0x90, 60, 0};
   currentpacket = MIDIPacketListAdd(packetlist, sizeof(buffer), 
         currentpacket, timestamp, MESSAGESIZE, noteoff);

   // send the MIDI data and exit immediately
   playPacketListOnAllDevices(midiout, packetlist);

   if (status = MIDIPortDispose(midiout)) {
      printf("Error trying to close MIDI output port: %d\n", status);
//      printf("%s\n", GetMacOSStatusErrorString(status));
      exit(status);
   }
   midiout = NULL;

   if (status = MIDIClientDispose(midiclient)) {
      printf("Error trying to close MIDI client: %d\n", status);
//      printf("%s\n", GetMacOSStatusErrorString(status));
      exit(status);
   }
   midiclient = NULL;
#endif

   return 0;
}
