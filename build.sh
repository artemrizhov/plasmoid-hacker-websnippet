#!/bin/bash

rm hacker-websnippet-0.1.plasmoid
zip -r hacker-websnippet-0.1.plasmoid contents metadata.desktop
plasmapkg -r hacker-websnippet
plasmapkg -i hacker-websnippet-0.1.plasmoid
