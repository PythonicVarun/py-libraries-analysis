import asyncio
from unittest.mock import MagicMock

async def reproduce_async_orm_bug():
    print("Simulating async ORM scenario where query returns no results...")
    # Simulate the result object returned by session.scalars()
    mock_result = MagicMock()
    # first() returns None when no rows found
    mock_result.first.return_value = None
    
    # This represents: result = await session.scalars(...)
    result = mock_result
    
    # This represents: a1 = result.first()
    a1 = result.first()
    
    print(f"a1 is: {a1}")
    
    try:
        # This represents: a1.data = "new data"
        print("Attempting to access a1.data...")
        a1.data = "new data"
    except AttributeError as e:
        print(f"Caught expected AttributeError: {e}")
        print("Verified: Bug reproduced (missing null check for 'first()' result)")

if __name__ == "__main__":
    asyncio.run(reproduce_async_orm_bug())
