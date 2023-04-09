"""Custom listings mutation and view."""
from typing import Annotated, List  # , Optional
from fastapi import Depends, APIRouter, HTTPException, status
# , HTTPException, status

from modules.database.db import get_all_custom_listings, \
    create_custom_listing, get_custom_listing, \
    get_all_custom_listings_by_company, get_lowest_bid, \
    declare_custom_listing_winner, place_bid, withdraw_bid, get_bid_list
# from modules.database.models import User
from modules.fastapi_utils import UserModel, CustomListingModel, \
    CustomListingCreateModel, PostRequestResponseModel
from .tools import get_current_user


router = APIRouter()


@router.get("/listings", response_model=List[CustomListingModel])
async def all_listings_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    active: bool | None = None
):
    """Return Custom Listings (all or be active bool key)."""
    if active is None:
        return await get_all_custom_listings()
    return await get_all_custom_listings(active=active)


@router.get("/listings/by-company", response_model=List[CustomListingModel])
async def all_listings_by_company_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    inn: int,
    active: bool | None = None
):
    """Return Custom Listings by a company (all or be active bool key)."""
    if active is None:
        return await get_all_custom_listings()
    return await get_all_custom_listings_by_company(inn, active=active)


@router.get("/listing", response_model=CustomListingModel)
async def listing_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    trackingId: int,
    lot: int
):
    """Return Custom Listing by trackingId."""
    try:
        listing = await get_custom_listing(trackingId, lot)
    except ValueError:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("/listing", response_model=PostRequestResponseModel)
async def listing_create(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    listing: CustomListingCreateModel
):
    """Create new Custom Listing."""
    try:
        await create_custom_listing(user_email=current_user.username,
                                    trackingId=listing.trackingId,
                                    lot=listing.lot,
                                    kind=listing.kind,
                                    name=listing.name,
                                    description=listing.description,
                                    base_price=listing.basePrice,
                                    ts_end=listing.tsEnd)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="Some of the user's company fields are null",
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A listing with the same Tracking ID and Lot already exists"
        )

    return {"message": "Listing created successfully",
            "status": 0}


@router.get("/listing/lowest-bid")
async def lowest_bid_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    trackingId: int,
    lot: int
):
    """Get the lowest bid for a Custom Listing.

    If none exist, get the basePrice.
    """
    try:
        lowest_bid = await get_lowest_bid(trackingId, lot)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing is not found",
        )
    return lowest_bid


@router.post("/listing/declare-winner",
             response_model=PostRequestResponseModel)
async def listing_winner_write(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    trackingId: int,
    lot: int,
    winner_inn: int
):
    """Declare the bidding's winner by their INN.

    Return HTTP 404 NOT FOUND if the bid from winner_inn was not found.
    Return HTTP 401 UNAUTHORIZED if the request is not from the \
listing's owner.
    """
    try:
        await declare_custom_listing_winner(current_user.username,
                                            trackingId, lot,
                                            winner_inn)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bid from the INN was not found in the database",
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Custom Listing does not belong to the user",
        )
    return {"message": "Winner selected successfully",
            "status": 0}


@router.post("/listing/bid", response_model=PostRequestResponseModel)
async def listing_bid_write(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    tracking_id: int,
    lot: int,
    bid: float
):
    """Place a bid on a Custom Listing.

    Return HTTP 409 CONFLICT if the bid was already placed.
    """
    try:
        await place_bid(current_user.username,
                        tracking_id, lot,
                        bid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A bid from this INN was already placed; remove it first",
        )
    return {"message": "Bid placed successfully",
            "status": 0}


@router.get("/listing/bids")
async def listing_bids_read(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    listing_tracking_id: int,
    lot: int
):
    """Get sorted biddings for a listing."""
    return await get_bid_list(listing_tracking_id, lot)


@router.post("/listing/bid/withdraw", response_model=PostRequestResponseModel)
async def listing_bid_withdraw(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    trackingId: int,
    lot: int
):
    """Remove a bid on a Custom Listing.

    Return HTTP 404 NOT FOUND if the bid was not found.
    """
    try:
        await withdraw_bid(current_user.username,
                           trackingId, lot)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A bid from this INN was not found",
        )
    return {"message": "Withdrawn bid successfully",
            "status": 0}
