import os
from dataclasses import dataclass

@dataclass
class Provider:
    name: str
    env_key: str
    @property
    def configured(self) -> bool:
        return bool(os.getenv(self.env_key))

class ProviderRouter:
    def __init__(self):
        self.image=[Provider('image_provider_1','IMAGE_PROVIDER_1_KEY'),Provider('image_provider_2','IMAGE_PROVIDER_2_KEY'),Provider('image_provider_3','IMAGE_PROVIDER_3_KEY')]
        self.video=[Provider('video_provider_1','VIDEO_PROVIDER_1_KEY'),Provider('video_provider_2','VIDEO_PROVIDER_2_KEY')]
        self.voice=[Provider('voice_provider_1','VOICE_PROVIDER_1_KEY'),Provider('voice_provider_2','VOICE_PROVIDER_2_KEY')]
    def status(self):
        def group(items): return [{'provider':p.name,'configured':p.configured} for p in items]
        return {'image':group(self.image),'video':group(self.video),'voice':group(self.voice)}
