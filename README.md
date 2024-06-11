### websockets-notifications demo

#### How to set JWK public key to validate jwt tokens
One of the options:
1. By setting the key as an environment variable named `JWT_PUBLIC_KEY`.
2. By placing the key in a file named `jwt_public_key.pem` inside the `secrets` folder in repo root.

If both options are set, the application will not start.
