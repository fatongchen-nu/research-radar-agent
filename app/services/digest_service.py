from app.schemas.digests import DailyDigestRead, digest_stub


class DigestService:
    async def get_today_digest(self, topic_id: str) -> DailyDigestRead:
        return digest_stub(topic_id)


_digest_service = DigestService()


def get_digest_service() -> DigestService:
    return _digest_service
