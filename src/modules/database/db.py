"""SQLAlchemy database management."""

from typing import Optional, List
from .models import User, CustomListing, CustomListingBid, \
    UserAchievements, Metric, TaskGoal, Task, Script, \
    StatisticsProto
# from .models import Achievement
from motor.motor_asyncio import AsyncIOMotorClient
# from pydantic import BaseModel
from beanie import init_beanie  # Document, Indexed,
from beanie.odm.enums import SortDirection
from datetime import datetime


async def init_db(mongodb_user: str,
                  mongodb_pass: str,
                  mongodb_host: str,
                  mongodb_port: str):
    """Initialize the database manager.

    Pass MongoDB Credentials to initialize this manager.
    """
    client = AsyncIOMotorClient(f"mongodb://{mongodb_user}:\
{mongodb_pass}@{mongodb_host}:{mongodb_port}")
    await init_beanie(database=client.rlt_hack,
                      document_models=[User,
                                       UserAchievements,
                                       CustomListing,
                                       CustomListingBid,
                                       Metric,
                                       TaskGoal,
                                       Task,
                                       Script,
                                       StatisticsProto])  # type: ignore


async def is_user(user_email: str) -> bool:
    """Check if the user exists in the database."""
    return await User.find_one(User.email == user_email) is not None


async def is_company(company_inn: int) -> bool:
    """Check if the company exists in the database."""
    return await User.find_one(User.companyInn == company_inn) is not None


async def is_company_accessible(user_email: str, company_inn: int) -> bool:
    """Check if the company INN is free or belongs to the user."""
    owner = await User.find_one({"companyInn": company_inn})
    if owner is None:
        return True
    if owner.email == user_email:
        return True
    return False


async def is_company_owner(user_email: str, company_inn: int) -> bool:
    """Check if the user owns the company INN."""
    return await User.find_one(User.email == user_email,
                               User.companyInn == company_inn) is not None


async def add_user(email: str,
                   password_hash: str,
                   name: str,
                   surname: str,
                   phone_number: int,
                   country: Optional[str],
                   city: Optional[str]):
    """Add a user to the database."""
    user = User(email=email,
                passwordHash=password_hash,
                firstName=name,
                lastName=surname,
                phoneNumber=phone_number,
                country=country,
                city=city,
                companyInn=None,
                companyName=None)
    await User.insert_one(user)


async def get_user(user_email: str) -> User | None:
    """Get the user from the database."""
    user = await User.find_one(User.email == user_email)
    return user


async def get_password_hash(user_email: str) -> str:
    """Get password hash stored in the database."""
    user = await User.find_one(User.email == user_email)
    if user is None:
        raise ValueError("User does not exist")
    return user.passwordHash


async def update_user_password(user_email: str, password_hash: str):
    """Update the user password in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.passwordHash: password_hash}))


async def update_user_email(user_email: str, new_email: str):
    """Update the user's email in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.email: new_email}))


async def update_user_first_name(user_email: str, name: str):
    """Update the user's name in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.firstName: name}))


async def update_user_last_name(user_email: str, surname: str):
    """Update the user's surname in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.lastName: surname}))


async def update_user_phone_number(user_email: str, phone_number: int):
    """Update the user's phone number in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.phoneNumber: phone_number}))  # type: ignore


async def update_user_country(user_email: str, country: str | None):
    """Update the user's country in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.country: country}))  # type: ignore


async def update_user_city(user_email: str, city: str | None):
    """Update the user's city in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.city: city}))  # type: ignore


async def set_user_company_name(user_email: str, company_name: str | None):
    """Set user's company name in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.companyName: company_name}))  # type: ignore


async def set_user_company_inn(user_email: str, company_inn: int | None):
    """Set user's company INN in the database."""
    await (User.find_one(User.email == user_email)
           .set({User.companyInn: company_inn}))  # type: ignore


async def get_user_company(user_email: str) -> dict:
    """Get the user companies from the database."""
    user = await User.find_one(User.email == user_email)
    if user is None:
        raise ValueError("User does not exist")
    return {"name": user.companyName,
            "inn": user.companyInn}


async def get_company_name_by_inn(company_inn: int) -> str | None:
    """Get company name by its INN."""
    company = await User.find_one(User.companyInn == company_inn)
    if company is None:
        raise ValueError("Company not found")
    return company.companyName


# region Custom Listings
async def custom_listing_belongs_to_user(user_email: str,
                                         listing_tracking_id: int,
                                         listing_lot: int) -> bool:
    """Check if the Custom Listing belongs to the user."""
    company_inn = (await get_user_company(user_email))["inn"]
    if company_inn is None:
        raise ValueError("User has no INN")
    return await CustomListing.find_one(
        CustomListing.companyInn == company_inn,
        CustomListing.trackingId == listing_tracking_id,
        CustomListing.lot == listing_lot) is not None


async def custom_listing_exists(listing_tracking_id: int,
                                listing_lot: int) -> bool:
    """Check if the Custom Listing exists."""
    return await CustomListing.find_one(
        CustomListing.trackingId == listing_tracking_id,
        CustomListing.lot == listing_lot) is not None


async def create_custom_listing(user_email: str,
                                trackingId: int,
                                lot: int,
                                kind: str,
                                name: str,
                                description: str,
                                base_price: float,
                                ts_end: datetime):
    """Create a new Custom Listing from the user's company."""
    company_inn = (await get_user_company(user_email))["inn"]
    if company_inn is None:
        raise ValueError("User has no INN")
    if await custom_listing_exists(trackingId, lot):
        raise KeyError("Listing already exists")
    listing = CustomListing(trackingId=trackingId,
                            lot=lot,
                            kind=kind,
                            name=name,
                            description=description,
                            companyInn=company_inn,
                            basePrice=base_price,
                            dynamic=0,
                            isActive=True,
                            tsEnd=ts_end)
    await CustomListing.insert_one(listing)


async def mut_custom_listing_is_active(user_email: str,
                                       listing_tracking_id: int,
                                       listing_lot: int,
                                       active: bool):
    """Activate or deactivate a Custom Listing."""
    if not await is_company_owner(user_email, listing_tracking_id):
        raise ValueError("User does not own the listing")
    await (CustomListing.find_one(CustomListing.trackingId
                                  == listing_tracking_id,
                                  CustomListing.lot == listing_lot)
           .set({CustomListing.isActive: active}))  # type: ignore


async def get_custom_listing(listing_tracking_id: int,
                             lot: int,
                             set_bid_dynamics: bool
                             = True) -> CustomListing | None:
    """Get a specific Custom Listing."""
    if set_bid_dynamics:
        await set_bid_dynamic(listing_tracking_id, lot,
                              await get_bid_dynamic(listing_tracking_id, lot))
    listing = await CustomListing.find_one(CustomListing.trackingId
                                           == listing_tracking_id,
                                           CustomListing.lot == lot)
    if listing is None:
        raise ValueError("Listing not found")
    return listing


async def get_all_custom_listings(active: bool | None = None,
                                  set_bid_dynamics: bool = True):
    """Get all Custom Listings (all or active/!active)."""
    if set_bid_dynamics:
        await set_all_bid_dynamics()
    if active is None:
        return await CustomListing.find_many().to_list()
    return await (CustomListing.find(CustomListing.isActive == active)
                  .to_list(None))


async def get_all_custom_listings_by_company(inn: int,
                                             active: bool | None = None):
    """Get all Custom Listings by company (all or active/!active)."""
    if active is None:
        return await CustomListing.find_many(CustomListing
                                             .companyInn == inn).to_list()
    return await (CustomListing
                  .find(CustomListing.companyInn == inn,
                        CustomListing.isActive == active)).to_list()


async def bid_exists(user_email: str,
                     listing_tracking_id: int,
                     listing_lot: int) -> bool:
    """Check if a bid from the user's company exists on a Custom Listing."""
    bidder_inn = (await get_user_company(user_email))["inn"]
    return (await CustomListingBid.find_one(
        CustomListingBid.listingTrackingId == listing_tracking_id,
        CustomListingBid.listingLot == listing_lot,
        CustomListingBid.bidderInn == bidder_inn) is not None)


async def place_bid(user_email: str,
                    listing_tracking_id: int,
                    listing_lot: int,
                    bid_price: float):
    """Place bid on a Custom Listing."""
    if await bid_exists(user_email, listing_tracking_id, listing_lot):
        raise ValueError("Bid already exists")
    bidder_inn = (await get_user_company(user_email))["inn"]
    bid = CustomListingBid(listingTrackingId=listing_tracking_id,
                           listingLot=listing_lot,
                           bidderInn=bidder_inn,
                           bidPrice=bid_price)
    await CustomListingBid.insert_one(bid)


async def withdraw_bid(user_email: str,
                       listing_tracking_id: int,
                       listing_lot: int):
    """Withdraw bid from a Custom Listing."""
    if not await bid_exists(user_email, listing_tracking_id, listing_lot):
        raise ValueError("Bid does not exist")
    bidder_inn = (await get_user_company(user_email))["inn"]
    bid = await CustomListingBid.find_one(
        CustomListingBid.listingTrackingId == listing_tracking_id,
        CustomListingBid.listingLot == listing_lot,
        CustomListingBid.bidderInn == bidder_inn)
    if bid is not None:
        await CustomListingBid.delete(bid)


async def get_lowest_bid(listing_tracking_id: int,
                         listing_lot: int) -> float | None:
    """Get the lowest bid on a Custom Listing."""
    bids = await get_bid_list(listing_tracking_id,
                              listing_lot)
    if len(bids) == 0:
        listing = await get_custom_listing(listing_tracking_id,
                                           listing_lot,
                                           set_bid_dynamics=False)
        return listing.basePrice if listing else None
    return bids[0].bidPrice


async def get_bid_dynamic(listing_tracking_id: int,
                          listing_lot: int) -> int:
    """Get listing dynamic (decreasing, increasing, stale)."""
    base = await get_custom_listing(listing_tracking_id, listing_lot,
                                    set_bid_dynamics=False)
    if base is None:
        raise ValueError
    base = base.basePrice
    current = await get_latest_bid(listing_tracking_id, listing_lot)
    if current is None:
        return 0
    if base == current:
        return 0
    if base > current:
        return -1
    return 1


async def set_bid_dynamic(listing_tracking_id: int,
                          listing_lot: int,
                          dynamic: int):
    """Set bid dynamic for Custom Listing."""
    await (CustomListing.find_one(CustomListing.trackingId
                                  == listing_tracking_id,
                                  CustomListing.lot == listing_lot)
           .set({CustomListing.dynamic: dynamic}))  # type: ignore


async def set_all_bid_dynamics():
    """Set bid dynamics for all Custom Listings."""
    listings = await get_all_custom_listings(set_bid_dynamics=False)
    for listing in listings:
        await set_bid_dynamic(listing.trackingId, listing.lot,
                              await get_bid_dynamic(listing.trackingId,
                                                    listing.lot))


async def get_latest_bid(listing_tracking_id: int,
                         listing_lot: int) -> float | None:
    """Get the latest bid on a Custom Listing."""
    bid = (await CustomListingBid
           .find_one(CustomListingBid.listingTrackingId
                     == listing_tracking_id,
                     CustomListingBid.listingLot == listing_lot))
    if bid is None:
        return None
    return bid.bidPrice


async def get_bid_list(listing_tracking_id: int,
                       listing_lot: int) -> List[CustomListingBid]:
    """Get all bids for a listing."""
    bids = await (CustomListingBid
                  .find(CustomListingBid.listingTrackingId
                        == listing_tracking_id,
                        CustomListingBid.listingLot == listing_lot)
                  .sort((CustomListingBid.bidPrice,
                         SortDirection.ASCENDING))  # type: ignore
                  .to_list(None))
    return bids


async def declare_custom_listing_winner(user_email: str,
                                        listing_tracking_id: int,
                                        listing_lot: int,
                                        winner_inn: int):
    """Declare a winner on a Custom Listing."""
    if not await bid_exists(user_email, listing_tracking_id, listing_lot):
        raise ValueError("Bid does not exist")
    if not await custom_listing_belongs_to_user(user_email,
                                                listing_tracking_id,
                                                listing_lot):
        raise KeyError("Custom listing does not belong to the user")
    # Set Custom Listing's winnerInn to the winner's INN
    await (CustomListing.find_one(
        CustomListing.trackingId == listing_tracking_id,
        CustomListing.lot == listing_lot)
        .set({CustomListing.winnerInn: winner_inn,
              CustomListing.isActive: False}))  # type: ignore


async def get_won_custom_listings(user_email: str) -> list:
    """Get all Custom Listings won by the user's company."""
    company_inn = (await get_user_company(user_email))["inn"]
    return await CustomListing.find(
        CustomListing.winnerInn == company_inn).to_list(None)
# endregion


# region Administrative privileges
async def elevate_privileges(user_email: str):
    """Elevate user's privileges to administrative."""
    (await User.find_one(User.email == user_email)
     .set({User.isAdmin: True}))  # type: ignore


async def is_admin(user_email: str) -> bool:
    """Check whether the user has administrative privileges."""
    return (await User.find_one(User.email ==
                                user_email)).isAdmin  # type: ignore
# endregion


# region Statistics
async def get_daily_statistics() -> dict | None:
    """Get daily statistics in JSON-like format."""
    stats = await StatisticsProto.find_one()
    if stats is None:
        return None
    return stats.daily  # type: ignore # type.ignore


async def get_monthly_statistics() -> dict | None:
    """Get monthly statistics in JSON-like format."""
    stats = await StatisticsProto.find_one()
    if stats is None:
        return None
    return stats.monthly  # type: ignore # type.ignore


async def get_yearly_statistics() -> dict | None:
    """Get yearly statistics in JSON-like format."""
    stats = await StatisticsProto.find_one()
    if stats is None:
        return None
    return stats.yearly  # type: ignore # type.ignore
# endregion


# region Achievements
async def get_all_scripts() -> List[Script]:
    """Get all Scripts."""
    return await Script.find().to_list(None)
# endregion
