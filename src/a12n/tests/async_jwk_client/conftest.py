import pytest

from respx import MockRouter
from respx import Route

from a12n.jwk_client import AsyncJWKClient

JWKS_URL = "https://auth.test.com/auth/realms/test-realm/protocol/openid-connect/certs"


@pytest.fixture
def expired_token():
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNMcjhuTjh1R29wUElMZlFvUGpfRCJ9.eyJpc3MiOiJodHRwczovL2Rldi1wcm50ZG1vMTYzc2NsczR4LnVzLmF1dGgwLmNvbS8iLCJhdWQiOiIxV1NiR1hGUnlhS0NsTHJvWHZteTlXdndrZUtHb1JvayIsImlhdCI6MTY5ODUyODU1OSwiZXhwIjoxNjk4NTI4ODU5LCJzdWIiOiJhdXRoMHw2NTNjMzI2MGEzMDQ0OGM1OTRhNjllMTIiLCJzaWQiOiI5MEZ3WFNDSFUtd0N3QmY0Y1YyQ3NZTnpBMldieDNUcSIsIm5vbmNlIjoiZTIxZWVhNTljNGY1MDg0N2Q3YzFhOGUzZjQ0NjVjYTcifQ.FO_xoMA9RGI7uAVauv00-zdORgkvCwyWfeAPd7lmU_nKzGp5avPa2MN66S0fjLKOxb8tgzrfpXYLUhDl1nqUvtj1A54-PfNW0n0ctdn2zk_CCOxsAjKyImlIgq7Y4DIuil0wikj7FdoWkB-bCBrKs7JaOoWkSHws9uQxRyvZzBwPHExW0myHWvB3G0x8g23PfSv2oALbvXBp0OAniGwru2Br9e2iXCVyGAUMTCpQmjPDAyfeYXGxF9BhxuX3e-GL80oyngBQK0kTxw-2Xz8LDSC-MI2jTs1gUo9qdVrg_1fzQtvAW9LGaWg5L_CJe92ZH3l1fBPfSh7Gc6uBtwF-YA"


@pytest.fixture
def token():
    # The token won't expire in ~100 years (expiration date 2123-10-05, it's more than enough to rely on it in test)
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNMcjhuTjh1R29wUElMZlFvUGpfRCJ9.eyJpc3MiOiJodHRwczovL2Rldi1wcm50ZG1vMTYzc2NsczR4LnVzLmF1dGgwLmNvbS8iLCJhdWQiOiIxV1NiR1hGUnlhS0NsTHJvWHZteTlXdndrZUtHb1JvayIsImlhdCI6MTY5ODUyODE3MCwiZXhwIjo0ODUyMTI4MTcwLCJzdWIiOiJhdXRoMHw2NTNjMzI2MGEzMDQ0OGM1OTRhNjllMTIiLCJzaWQiOiI5MEZ3WFNDSFUtd0N3QmY0Y1YyQ3NZTnpBMldieDNUcSIsIm5vbmNlIjoiMTVhNWI2M2Y3MzI5MDcwMmU3MGViZmJlMDc5ODgxYmIifQ.FQYBaTnjKJHcskRl1WsB4kKQmyvXRcG8RDWlB2woSbzukZx7SnWghC1qRhYeqOLBUBpe3Iu_EzxgF26YDZJ28bKKNgL4fVmYak3jOg2nRP2lulrkF8USmkqT9Vx85hlIEVCisYOS6DJE0bHJL5WbHjCmDjQ6RGRyVZ3s6UPFXIwe2CMC_egAdWrsLYrgA1mqozQhwLJN2zSuObkDffkpHbX9XXB225v3-ryY-Rr0rPh9AOfKtEeMUEmNG0gsGyIbi0DoPDjAxlxCDx7ULVSChIKhUv4DKICqrqzHyopA7oE8LlpDbPTshQsL6L4u1EwUT7maP9VTcEQUTnp3Cu5msw"


@pytest.fixture
def matching_kid_data():
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "n": "oIQkRCY4X-_ItMUPt65wVIGewOJfjMhlu6HG_rHik5-dTK0o6oyUne2Gevetn2Vrn8NSIaARobLZ8expuJBYDS121w_RloC6MCuzlc-j_nHj-BcBOCqGWPVwKX4un0HueD3aW3buqzYcmX_9LhdSE8ARyN0S9O6RbYWDCTKFhrRXtIP4wzP8vdPGXGurtGIiBbhVCK1LHG2lO5Gt8IIQ_DAcX6swnXCfbHwR1OXc9Do06o8c7ZsZdjMty5b4Fpv8rAKA-HTP_One4yhKtqCMYs3_gcTeQdHi-0w634VnpdzC_0f_MMzNIgvXC8VdJgkGpa6jLBp3mTqaFUdkAXFYlw",
                "e": "AQAB",
                "kid": "3Lr8nN8uGopPILfQoPj_D",
                "x5t": "f93zLhSTsgVJiS9JA0x8sHkaLMg",
                "x5c": [
                    "MIIDHTCCAgWgAwIBAgIJA2x2yGZ3QbP7MA0GCSqGSIb3DQEBCwUAMCwxKjAoBgNVBAMTIWRldi1wcm50ZG1vMTYzc2NsczR4LnVzLmF1dGgwLmNvbTAeFw0yMzEwMjcyMTU0MDhaFw0zNzA3MDUyMTU0MDhaMCwxKjAoBgNVBAMTIWRldi1wcm50ZG1vMTYzc2NsczR4LnVzLmF1dGgwLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKCEJEQmOF/vyLTFD7eucFSBnsDiX4zIZbuhxv6x4pOfnUytKOqMlJ3thnr3rZ9la5/DUiGgEaGy2fHsabiQWA0tdtcP0ZaAujArs5XPo/5x4/gXATgqhlj1cCl+Lp9B7ng92lt27qs2HJl//S4XUhPAEcjdEvTukW2FgwkyhYa0V7SD+MMz/L3Txlxrq7RiIgW4VQitSxxtpTuRrfCCEPwwHF+rMJ1wn2x8EdTl3PQ6NOqPHO2bGXYzLcuW+Bab/KwCgPh0z/zp3uMoSragjGLN/4HE3kHR4vtMOt+FZ6Xcwv9H/zDMzSIL1wvFXSYJBqWuoywad5k6mhVHZAFxWJcCAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUs39B3IFR+w1DjzejWvr7ZnNU9DswDgYDVR0PAQH/BAQDAgKEMA0GCSqGSIb3DQEBCwUAA4IBAQBimrxvOHAssNkEU7r5aTiz0lvtlshUe4zN6r9pqA7P0m0OoxJMiEkGrtPblVIL8hNSRcSsD0AmlA/dfP8RR39BY44ac4KLh5WfCRsi5LXENqmPeNvFiVGKL3UBvtpp6KIc9mT1vFY9Jhdh8srF3AS9STFD9O1/qexevvgqkq4ZCng+kHuRP9C7eU3yQUQeZ9QYWloZuPaNe7DT3J6v7OW1gy41xjUpL0GisRcCqsVI+dzHDYi1MFfvmUwxcmtg8GXYexuR6FUkgocdRXQsDQ1qIhS9M54WVEEgC+fat25Kb/Ca59GO3okJ4suqMAXKCtlbVh3JUgBsCjBdbk0tYwp0"
                ],
                "alg": "RS256",
            },
        ]
    }


@pytest.fixture
def not_matching_kid_data():
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "n": "zB0xsH539lpLVejR6Hq1bHN3EzDt_0tJyr5JVHz3GSnNYAaZzkqL7HyLlhwttl7_bRyZJeZ8X6aasBxVK2JCDc9U-0KMJXmSoJs1oWYRo79DqdzCXK3ZYXcgkvI9OWF1qVx76vbZVwiRv5qUzpINdLnsX2CXChyd0LFkg14bYrSfdN-eMmG1PXtHZufeKG6HW17PFXS7OwesMQIfQ9kFfSvgFkJgkNM0o6NaeB-ZPDvzfKmmpBXjtGcze0A56NdQ7Z42DRDURROS82sPISrX-iAt93tZ1F0IW_U4niIYc6NFcWPPXpQpiVDDwdrz-L1H63mSUDSDFsWVcv2xWry6kQ",
                "e": "AQAB",
                "kid": "ICOpsXGmpNaDPiljjRjiE",
                "x5t": "1GDK6kGV6HvZ1m_-VdSKIFNEtEU",
                "x5c": [
                    "MIIDHTCCAgWgAwIBAgIJYH5BBAgUHJCVMA0GCSqGSIb3DQEBCwUAMCwxKjAoBgNVBAMTIWRldi1wcm50ZG1vMTYzc2NsczR4LnVzLmF1dGgwLmNvbTAeFw0yMzEwMjcyMTU0MDlaFw0zNzA3MDUyMTU0MDlaMCwxKjAoBgNVBAMTIWRldi1wcm50ZG1vMTYzc2NsczR4LnVzLmF1dGgwLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMwdMbB+d/ZaS1Xo0eh6tWxzdxMw7f9LScq+SVR89xkpzWAGmc5Ki+x8i5YcLbZe/20cmSXmfF+mmrAcVStiQg3PVPtCjCV5kqCbNaFmEaO/Q6ncwlyt2WF3IJLyPTlhdalce+r22VcIkb+alM6SDXS57F9glwocndCxZINeG2K0n3TfnjJhtT17R2bn3ihuh1tezxV0uzsHrDECH0PZBX0r4BZCYJDTNKOjWngfmTw783yppqQV47RnM3tAOejXUO2eNg0Q1EUTkvNrDyEq1/ogLfd7WdRdCFv1OJ4iGHOjRXFjz16UKYlQw8Ha8/i9R+t5klA0gxbFlXL9sVq8upECAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUD06HTot2wVkYAi77ZUSLnBDXJx8wDgYDVR0PAQH/BAQDAgKEMA0GCSqGSIb3DQEBCwUAA4IBAQB+YY5dSdTqsO1ErV+ZusJ/+z+WZ/Kf+rBhX7pbPGdL00mbwyF5kKc1g9Nd2S6Uz+w5FrU7cv3ABkppQNK/07ipyad9EOEd1rWiVp9/f18VB4OUqSgxZyXrAuqEVTFTPL3wwBOG/cw3pYtF2DZ26Y5tIxic4T+Z+dmtxZm/7387XrGisUTngdQvs3X+3xvjou2Z+pCIP1+Qe14S+WM77ZMa62O/rajtdsvOXWGh68oKitzaE0/gKpGjP8mBkd5Taxl+MLXU+Ea/RvVZOtvtOomANyyEXRX2WBN90djFqdlTF7Lhb7X6OTvZGt9ZmgXDtVGgBkeJxJOgFEAyDpn3ErWx"
                ],
                "alg": "RS256",
            },
        ]
    }


@pytest.fixture
def mock_jwk_endpoint(respx_mock: MockRouter):
    return respx_mock.get(JWKS_URL)


@pytest.fixture
def mock_success_response(mock_jwk_endpoint: Route, matching_kid_data):
    return mock_jwk_endpoint.respond(json=matching_kid_data)


@pytest.fixture
def jwk_client():
    return AsyncJWKClient(jwks_url=JWKS_URL, supported_signing_algorithms=["RS256"])
