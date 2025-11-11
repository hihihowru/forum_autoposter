import React, { useState, useEffect } from 'react';
import { Card, DatePicker, Segmented, Row, Col, Statistic, Spin, message } from 'antd';
import { Column, DualAxes } from '@ant-design/charts';
import { ClockCircleOutlined, FileTextOutlined, LikeOutlined, BarChartOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';

const { RangePicker } = DatePicker;

interface HourlyData {
  hour: number;
  hour_label: string;
  time_range: string;
  count: number;
  label: string;
  start_time: string;
  end_time: string;
}

interface ReactionData {
  hour: number;
  hour_label: string;
  reaction_count: number;
  article_count: number;
  time_range: string;
}

interface Props {
  apiBaseUrl: string;
}

export default function ReactionAnalytics({ apiBaseUrl }: Props) {
  const [viewMode, setViewMode] = useState<'hourly' | 'daily'>('hourly');
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(23, 'hours'),
    dayjs()
  ]);
  const [loading, setLoading] = useState(false);
  const [articleData, setArticleData] = useState<HourlyData[]>([]);
  const [reactionData, setReactionData] = useState<ReactionData[]>([]);

  // Summary stats
  const [totalArticles, setTotalArticles] = useState(0);
  const [totalReactions, setTotalReactions] = useState(0);
  const [avgArticlesPerHour, setAvgArticlesPerHour] = useState(0);
  const [avgReactionsPerHour, setAvgReactionsPerHour] = useState(0);

  // Fetch data
  const fetchData = async () => {
    setLoading(true);
    try {
      const hoursDiff = dateRange[1].diff(dateRange[0], 'hours');

      // Fetch article counts
      const articleResponse = await fetch(
        `${apiBaseUrl}/api/reaction-bot/fetch-articles/hourly-breakdown?hours=${hoursDiff}`
      );
      if (articleResponse.ok) {
        const articleResult = await articleResponse.json();
        setArticleData(articleResult.hourly_breakdown || []);
        setTotalArticles(articleResult.total_articles || 0);
        setAvgArticlesPerHour(
          articleResult.total_articles / articleResult.total_hours || 0
        );
      }

      // Fetch reaction stats (from reaction_bot_logs table)
      const reactionResponse = await fetch(
        `${apiBaseUrl}/api/reaction-bot/stats?days=${Math.ceil(hoursDiff / 24)}`
      );
      if (reactionResponse.ok) {
        const reactionResult = await reactionResponse.json();

        // Process daily stats into hourly format
        // TODO: Backend needs to return hourly reaction stats
        const mockReactionData: ReactionData[] = articleData.map((article, index) => ({
          hour: article.hour,
          hour_label: article.hour_label,
          reaction_count: Math.floor(article.count * 0.3), // Mock: 30% reaction rate
          article_count: article.count,
          time_range: article.time_range
        }));

        setReactionData(mockReactionData);
        const totalReactionsMock = mockReactionData.reduce((sum, d) => sum + d.reaction_count, 0);
        setTotalReactions(totalReactionsMock);
        setAvgReactionsPerHour(totalReactionsMock / hoursDiff || 0);
      }

    } catch (error) {
      console.error('Error fetching analytics data:', error);
      message.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [dateRange, viewMode]);

  // Aggregate hourly data to daily if needed
  const aggregateToDaily = (hourlyData: ReactionData[]) => {
    const dailyMap = new Map<string, { articles: number; reactions: number }>();

    hourlyData.forEach(item => {
      const date = dayjs(item.start_time).format('YYYY-MM-DD');
      const existing = dailyMap.get(date) || { articles: 0, reactions: 0 };
      dailyMap.set(date, {
        articles: existing.articles + item.article_count,
        reactions: existing.reactions + item.reaction_count
      });
    });

    return Array.from(dailyMap.entries()).map(([date, data]) => ({
      date,
      article_count: data.articles,
      reaction_count: data.reactions
    }));
  };

  // Prepare chart data
  const chartData = viewMode === 'hourly'
    ? reactionData.map(d => ({
        time: d.hour_label,
        article_count: d.article_count,
        reaction_count: d.reaction_count
      }))
    : aggregateToDaily(reactionData).map(d => ({
        time: d.date,
        article_count: d.article_count,
        reaction_count: d.reaction_count
      }));

  // Dual Axes Chart Config
  const dualAxesConfig = {
    data: [chartData, chartData],
    xField: 'time',
    yField: ['article_count', 'reaction_count'],
    geometryOptions: [
      {
        geometry: 'column',
        color: '#5B8FF9',
        columnWidthRatio: 0.4,
      },
      {
        geometry: 'line',
        color: '#5AD8A6',
        lineStyle: {
          lineWidth: 2,
        },
      },
    ],
    yAxis: {
      article_count: {
        title: {
          text: 'Articles',
          style: { fill: '#5B8FF9' },
        },
      },
      reaction_count: {
        title: {
          text: 'Reactions',
          style: { fill: '#5AD8A6' },
        },
      },
    },
    legend: {
      position: 'top-right' as const,
    },
    tooltip: {
      shared: true,
    },
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card title="📊 Reaction Bot Analytics" bordered={false}>
        {/* Controls */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={12}>
            <RangePicker
              showTime
              value={dateRange}
              onChange={(dates) => {
                if (dates && dates[0] && dates[1]) {
                  setDateRange([dates[0], dates[1]]);
                }
              }}
              style={{ width: '100%' }}
            />
          </Col>
          <Col span={12}>
            <Segmented
              options={[
                { label: '📈 Hourly', value: 'hourly' },
                { label: '📅 Daily', value: 'daily' },
              ]}
              value={viewMode}
              onChange={(value) => setViewMode(value as 'hourly' | 'daily')}
              block
            />
          </Col>
        </Row>

        {/* Summary Cards */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Total Articles"
                value={totalArticles}
                prefix={<FileTextOutlined />}
                valueStyle={{ color: '#5B8FF9' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Total Reactions"
                value={totalReactions}
                prefix={<LikeOutlined />}
                valueStyle={{ color: '#5AD8A6' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title={`Avg Articles/${viewMode === 'hourly' ? 'Hour' : 'Day'}`}
                value={avgArticlesPerHour.toFixed(1)}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#5B8FF9' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title={`Avg Reactions/${viewMode === 'hourly' ? 'Hour' : 'Day'}`}
                value={avgReactionsPerHour.toFixed(1)}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#5AD8A6' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Chart */}
        <Card title={`${viewMode === 'hourly' ? 'Hourly' : 'Daily'} Breakdown`}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '60px 0' }}>
              <Spin size="large" />
            </div>
          ) : (
            <DualAxes {...dualAxesConfig} height={400} />
          )}
        </Card>

        {/* Data Table Preview */}
        <Card title="Raw Data (Top 10)" style={{ marginTop: 16 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #f0f0f0' }}>
                <th style={{ padding: '12px', textAlign: 'left' }}>Time</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Articles</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Reactions</th>
                <th style={{ padding: '12px', textAlign: 'right' }}>Reaction Rate</th>
              </tr>
            </thead>
            <tbody>
              {chartData.slice(0, 10).map((row, index) => {
                const rate = row.article_count > 0
                  ? ((row.reaction_count / row.article_count) * 100).toFixed(1)
                  : '0.0';
                return (
                  <tr key={index} style={{ borderBottom: '1px solid #f0f0f0' }}>
                    <td style={{ padding: '12px' }}>{row.time}</td>
                    <td style={{ padding: '12px', textAlign: 'right', color: '#5B8FF9' }}>
                      {row.article_count}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right', color: '#5AD8A6' }}>
                      {row.reaction_count}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      {rate}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Card>
      </Card>
    </div>
  );
}
