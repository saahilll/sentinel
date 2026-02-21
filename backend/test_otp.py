import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Request a magic link
        print("Requesting magic link + OTP...")
        r = await client.post("http://localhost:8000/api/auth/magic-link", json={"email": "test@example.com"})
        r.raise_for_status()
        print("Response:", r.json())
        print("Please check the backend logs for the actual OTP value.")

        # Wait for the user to copy the OTP from the backend terminal
        otp = input("Enter the 6-digit OTP from the backend logs: ")
        
        # Verify the OTP
        print("Verifying OTP...")
        verify_uri = "http://localhost:8000/api/auth/verify-otp"
        r = await client.post(verify_uri, json={"email": "test@example.com", "otp": otp, "remember_me": True})
        
        if r.status_code == 200:
            print("SUCCESS! OTP Verified.")
            print("Access Token:", r.json().get("access_token"))
        else:
            print("FAILED! OTP Verification failed:", r.text)

if __name__ == "__main__":
    asyncio.run(main())
