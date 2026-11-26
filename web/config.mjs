export default {
  "title": "Sanctions Ledger",
  "intro": "Search by name or regime, or compare how a source entry appeared in two saved copies of the list.",
  "eyebrow": "CANADIAN SANCTIONS / CONSOLIDATED SOURCE",
  "accent": "#775565",
  "tint": "#f0e5ec",
  "method": [
    "Global Affairs Canada’s consolidated XML is a reference list and has no force of law. The controlling regulations may change before the consolidated source is updated. Follow the linked regulation for legal interpretation.",
    "Entries are matched by regime, schedule and item number. Country-Pays is a regime label, not always a geographic country. Identity-field changes within the same slot are labelled source changes rather than assumed legal corrections.",
    "The first capture is a baseline, not thousands of new sanctions. Source listing date, source update date and our capture date have different meanings. Later absence from the file does not itself establish a legal delisting."
  ],
  "id": "sanctionsledger",
  "explorer-title": "Search the saved list",
  "cadence": "Daily automated collection. Source dates and capture dates are shown separately.",
  "facets": [
    {
      "key": "regime",
      "label": "Regime"
    },
    {
      "key": "kind",
      "label": "Entry type"
    },
    {
      "key": "listed_year",
      "label": "Source listing year"
    }
  ],
  "columns": [
    {
      "key": "name",
      "label": "Source-listed name"
    },
    {
      "key": "regime",
      "label": "Regime"
    },
    {
      "key": "kind",
      "label": "Type"
    },
    {
      "key": "schedule",
      "label": "Schedule"
    },
    {
      "key": "item",
      "label": "Item"
    },
    {
      "key": "listed_date",
      "label": "Source listing date"
    }
  ],
  "related": [
    {
      "label": "Corporate Ghosts",
      "url": "https://coolcode.ca/corporateghosts/"
    },
    {
      "label": "Lobby Trail",
      "url": "https://coolcode.ca/lobbytrail/"
    }
  ]
};
