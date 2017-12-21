#!/bin/bash
# Generate the key

echo "generating key..."
gpg --batch --gen-key $1
echo "key generated..."
echo "done"
#gpg --fingerprint ss1 > ss1_fingerprint.txt