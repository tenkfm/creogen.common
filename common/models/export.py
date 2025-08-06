import io, csv
from enum import Enum
from datetime import datetime
from typing import List, ClassVar, Optional
from pydantic import BaseModel, Field
from common.services.firebase.firebase_object import FirebaseObject


class TTExport(FirebaseObject):
    ALL_FIELDS: ClassVar[List[str]] = [
        "Campaign ID", "Campaign Status", "Campaign Name", "Advertising Objective",
        "Campaign type", "Sales destination", "Use catalog", "Product source",
        "iOS 14 Dedicated Campaign", "App profile page used", "Campaign Budget Type",
        "Campaign Budget Amount", "Campaign Budget Optimization", "Special ads categories",
        "Realtime API (RTA)", "Ad Group ID", "Ad Group Status", "Ad Group Name",
        "Interaction type", "Shop ads type", "Catalog ID", "Business Center ID of the catalog",
        "TikTok Shop code", "Business Center ID of the TikTok Shop", "Placement Types",
        "Placements", "Include search results", "Block List (Pangle)", "Optimization location",
        "TikTok Pixel ID", "Pixel Event", "App ID", "User Comment", "Video Download",
        "Allow video sharing", "Automated Creative Optimization", "Audience Targeting (VSA)",
        "Include audience ID", "Exclude audience ID", "Retarget audience type",
        "Date range (retarget audience)", "Custom audience", "Smart audience", "Location",
        "Gender", "Age", "Languages", "Spending power", "Household income",
        "Interest Category", "Video interactions", "Creator Category",
        "Creator-related Actions", "Hashtag interactions", "Additional interests",
        "Smart interests & behaviors", "Internet service provider", "Operating System",
        "Connection Type", "Carriers", "Device Price", "OS Versions", "Device model",
        "Category exclusions", "Vertical sensitivity", "Inventory filter",
        "Ad Group Budget Type", "Ad Group Budget Amount", "Start Time", "End Time",
        "Dayparting", "Optimization Goal", "In-App Event", "Secondary Goal",
        "Billing Method", "Click-through window", "View-through window",
        "Engaged view-through window", "Event count", "Frequency Cap", "Bid Strategy",
        "Bid", "Bid for oCPC/M", "Minimum ROAS", "Bid for Secondary Goal", "Delivery Type",
        "Ad ID", "Ad Status", "Ad Name", "Products type", "Product set ID", "Product ID",
        "Use TikTok Account", "Identity Type", "Identity ID",
        "Business Center ID of the identity", "Ad format", "Image Name", "Video Name",
        "Post ID", "Ad Music ID", "Only show as ad", "Catalog video template ID",
        "Destination Page Type (VSA)", "Destination", "Instant page ID", "Interactive add-on ID",
        "Text", "Call to action type", "Call to Action", "Playable ID",
        "Auto Ad - Image Name", "Auto Ad - Video Name", "Auto Ad - Text",
        "Auto ad - call to action type", "Auto Ad - Call to Action",
        "Website type", "Web URL", "Deeplink type", "Deeplink URL",
        "Fallback Type", "Fallback Website URL", "Impression Tracking URL",
        "Click Tracking URL", "TikTok website events", "TikTok app events",
        "TikTok offline events"
    ]
    
    def get_csv(self) -> str:
        rows = []
        for i in range(self.ad_groups_count):
            row = self.__generate_row(
                ad_group_name=f"Ad Group {i + 1}",
                ad_name=f"Ad_1",
                video_file_name=self.file_names[i] if i < len(self.file_names) else self.file_names[i % len(self.file_names)]
            )
            rows.append(row)
            
        return self.__generate_tiktok_csv(rows)


    def __generate_row(self, ad_group_name: str, ad_name: str, video_file_name: str):
        now_str = datetime.now().strftime("%Y/%m/%d %H:%M")
        return {
            "Campaign Status": "On",
            "Campaign Name": self.campaign_name,
            "Advertising Objective": "Sales",
            "Sales destination": "Website",
            "iOS 14 Dedicated Campaign": "Off",
            "Campaign Budget Type": "No Limit",
            "Campaign Budget Optimization": "Off",
            "Ad Group Status": "On",
            "Ad Group Name": ad_group_name,
            "Placement Types": "Select",
            "Placements": "TikTok",
            "Include search results": "Off",
            "Optimization location": "Website",
            "TikTok Pixel ID": self.pixel_id,
            "Pixel Event": self.pixel_event,
            "User Comment": "Off",
            "Video Download": "Off",
            "Allow video sharing": "Off",
            "Automated Creative Optimization": "Off",
            "Smart audience": "Off",
            "Location": ",".join(self.locations),
            "Gender": "All",
            "Age": "18-24,25-34,35-44,45-54,55+",
            "Languages": ",".join(self.languages),
            "Spending power": "All",
            "Household income": "All",
            "Smart interests & behaviors": "Off",
            "Internet service provider": "All",
            "Operating System": "All",
            "Connection Type": "All",
            "Carriers": "All",
            "Device Price": "All",
            "OS Versions": "All",
            "Device model": "All",
            "Inventory filter": "Full inventory",
            "Ad Group Budget Type": "Daily",
            "Ad Group Budget Amount": self.budget,
            "Start Time": now_str,
            "End Time": "No Limit",
            "Dayparting": "All Day",
            "Optimization Goal": "Conversion",
            "Billing Method": "oCPM",
            "Click-through window": "7-day click",
            "View-through window": "1-day view",
            "Event count": "Every",
            "Bid Strategy": "Cost Cap",
            "Bid for oCPC/M": self.bid,
            "Delivery Type": "Standard",
            "Ad Status": "On",
            "Ad Name": ad_name,
            "Use TikTok Account": "Off",
            "Identity Type": "Custom Identity",
            "Identity ID": self.identity_id,
            "Ad format": "Single video",
            "Video Name": video_file_name,
            "Text": self.text,
            "Call to action type": "Standard",
            "Call to Action": "Learn More",
            "Web URL": self.url,
            "TikTok website events": self.event_name,
        }
    
    def __generate_tiktok_csv(self, rows) -> str:
        """
        rows: list of dicts, где ключи — это те же самые имена колонок из ALL_FIELDS,
              а значения — строки, которые нужно записать.
        Возвращает строку с содержимым CSV (UTF-8 с BOM).
        """
        output = io.StringIO()
        output.write('\ufeff')
        writer = csv.DictWriter(output, fieldnames=self.ALL_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in self.ALL_FIELDS})
        return output.getvalue()
    
    
    user_id: Optional[str] = None
    publication_id: Optional[str] = None
    campaign_name: str
    ad_groups_count: int
    pixel_id: str
    pixel_event: str
    locations: List[str]
    languages: List[str]
    budget: float
    bid: float
    identity_id: str
    text: str
    url: str
    event_name: str
    file_names: List[str] = Field(default_factory=list)
    
    
    @staticmethod
    def collection_name():
        return "tt_exports"
    
    