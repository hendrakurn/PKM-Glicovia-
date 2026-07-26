export interface TopicResolution {
  prefix: string;
  topic: string;
  segments: string[];
  deviceCodeFromTopic?: string;
  topicIsUnderPrefix: boolean;
}

export function parseTopicResolution(topic: string, prefix: string): TopicResolution {
  const segments = topic.split('/').filter(Boolean);
  const prefixSegments = prefix.split('/').filter(Boolean);
  const topicIsUnderPrefix = prefixSegments.length === 0 || prefixSegments.every((segment, index) => segments[index] === segment);

  let deviceCodeFromTopic: string | undefined;
  if (topicIsUnderPrefix) {
    const remainder = segments.slice(prefixSegments.length);
    if (remainder.length > 0) {
      const readingsIndex = remainder.indexOf('readings');
      if (readingsIndex > 0) {
        deviceCodeFromTopic = remainder[readingsIndex - 1];
      } else {
        deviceCodeFromTopic = remainder[0];
      }
    }
  }

  return {
    prefix,
    topic,
    segments,
    deviceCodeFromTopic,
    topicIsUnderPrefix
  };
}
